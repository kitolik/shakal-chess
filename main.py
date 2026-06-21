import json
import uuid
import asyncio
import logging
import os
from typing import Dict, List, Optional

import chess
import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from html_templates import get_game_page, get_home_page

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Шахматы с чатом")


# ─────────────────────────────────────────────
#  Keep-alive: пинг самого себя каждые 5 минут
#  чтобы Render не усыплял бесплатный сервер
# ─────────────────────────────────────────────

async def keep_alive_task():
    """Каждые 5 минут делает GET-запрос на собственный /ping."""
    await asyncio.sleep(30)  # небольшая пауза после старта
    while True:
        try:
            # RENDER_EXTERNAL_URL автоматически задаётся Render'ом
            base_url = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:8000")
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{base_url}/ping")
                logger.info(f"[keep-alive] ping → {resp.status_code}")
        except Exception as e:
            logger.warning(f"[keep-alive] ошибка пинга: {e}")
        await asyncio.sleep(300)  # 5 минут


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(keep_alive_task())
    logger.info("Keep-alive задача запущена (интервал: 5 минут)")


# ─────────────────────────────────────────────
#  Классы для управления состоянием комнат
# ─────────────────────────────────────────────

class Player:
    def __init__(self, ws: WebSocket, name: str, color: Optional[str] = None):
        self.ws = ws
        self.name = name
        self.color = color  # "white" | "black" | None (зритель)


class Room:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.board = chess.Board()
        self.players: List[Player] = []
        self.chat_history: List[dict] = []

    def get_board_array(self) -> List[List[str]]:
        """Возвращает доску как двумерный массив 8x8."""
        grid = []
        for rank in range(7, -1, -1):  # 8-я горизонталь сверху
            row = []
            for file in range(8):
                piece = self.board.piece_at(chess.square(file, rank))
                if piece is None:
                    row.append("")
                else:
                    row.append(piece.symbol())  # заглавная=белая, строчная=чёрная
            grid.append(row)
        return grid

    def assign_color(self) -> Optional[str]:
        taken = {p.color for p in self.players}
        if "white" not in taken:
            return "white"
        if "black" not in taken:
            return "black"
        return None  # зритель

    def get_player(self, ws: WebSocket) -> Optional[Player]:
        for p in self.players:
            if p.ws is ws:
                return p
        return None

    def remove_player(self, ws: WebSocket):
        self.players = [p for p in self.players if p.ws is not ws]

    async def broadcast(self, message: dict):
        dead = []
        for player in self.players:
            try:
                await player.ws.send_json(message)
            except Exception:
                dead.append(player.ws)
        for ws in dead:
            self.remove_player(ws)

    def whose_turn(self) -> str:
        return "white" if self.board.turn == chess.WHITE else "black"


# ─────────────────────────────────────────────
#  Хранилище комнат
# ─────────────────────────────────────────────

rooms: Dict[str, Room] = {}


def get_or_create_room(room_id: str) -> Room:
    if room_id not in rooms:
        rooms[room_id] = Room(room_id)
    return rooms[room_id]


# ─────────────────────────────────────────────
#  HTTP-роуты
# ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home():
    return get_home_page()


@app.get("/room/{room_id}", response_class=HTMLResponse)
async def game_room(room_id: str):
    return get_game_page(room_id)


@app.post("/api/create-room")
async def create_room():
    room_id = str(uuid.uuid4())[:8]
    get_or_create_room(room_id)
    return {"room_id": room_id}


@app.get("/ping")
async def ping():
    """Эндпоинт для keep-alive пинга."""
    return {"status": "ok", "rooms": len(rooms)}


@app.get("/api/rooms")
async def list_rooms():
    result = []
    for rid, room in rooms.items():
        result.append({
            "room_id": rid,
            "players": len([p for p in room.players if p.color]),
            "spectators": len([p for p in room.players if not p.color]),
        })
    return result


# ─────────────────────────────────────────────
#  WebSocket
# ─────────────────────────────────────────────

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    room = get_or_create_room(room_id)

    try:
        init_data = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
        player_name = init_data.get("name", "Гость")[:30]
    except asyncio.TimeoutError:
        player_name = "Гость"
    except Exception:
        await websocket.close()
        return

    color = room.assign_color()
    player = Player(websocket, player_name, color)
    room.players.append(player)

    role_label = {"white": "⬜ Белые", "black": "⬛ Чёрные"}.get(color, "👁 Зритель")
    logger.info(f"[{room_id}] {player_name} подключился как {role_label}")

    await websocket.send_json({
        "type": "init",
        "board": room.get_board_array(),
        "color": color,
        "name": player_name,
        "turn": room.whose_turn(),
        "chat": room.chat_history[-50:],
    })

    join_msg = {
        "type": "chat",
        "sender": "🎲 Система",
        "text": f"{player_name} подключился как {role_label}",
        "system": True,
    }
    room.chat_history.append(join_msg)
    await room.broadcast(join_msg)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            # ── Чат ──────────────────────────────────
            if msg_type == "chat":
                text = str(data.get("text", "")).strip()[:500]
                if not text:
                    continue
                chat_msg = {
                    "type": "chat",
                    "sender": player_name,
                    "text": text,
                    "color": color,
                }
                room.chat_history.append(chat_msg)
                if len(room.chat_history) > 200:
                    room.chat_history = room.chat_history[-200:]
                await room.broadcast(chat_msg)

            # ── Ход ──────────────────────────────────
            elif msg_type == "move":
                if color != room.whose_turn():
                    await websocket.send_json({"type": "error", "text": "Сейчас не ваш ход!"})
                    continue
                if color is None:
                    await websocket.send_json({"type": "error", "text": "Зрители не могут ходить."})
                    continue

                from_sq = data.get("from")
                to_sq = data.get("to")
                promotion = data.get("promotion", "q")

                try:
                    uci = from_sq + to_sq
                    piece = room.board.piece_at(chess.parse_square(from_sq))
                    if (piece and piece.piece_type == chess.PAWN and to_sq[1] in ("1", "8")):
                        uci += promotion

                    move = chess.Move.from_uci(uci)
                    if move not in room.board.legal_moves:
                        raise ValueError("Нелегальный ход")

                    san = room.board.san(move)
                    room.board.push(move)

                    update = {
                        "type": "update",
                        "board": room.get_board_array(),
                        "turn": room.whose_turn(),
                        "last_move": {"from": from_sq, "to": to_sq},
                        "san": san,
                        "status": "ok",
                    }

                    if room.board.is_checkmate():
                        update["status"] = "checkmate"
                        update["winner"] = color
                    elif room.board.is_stalemate():
                        update["status"] = "stalemate"
                    elif room.board.is_check():
                        update["status"] = "check"

                    await room.broadcast(update)

                    move_msg = {
                        "type": "chat",
                        "sender": "♟ Игра",
                        "text": f"{player_name}: {san}",
                        "system": True,
                    }
                    room.chat_history.append(move_msg)
                    await room.broadcast(move_msg)

                except (ValueError, AttributeError) as e:
                    await websocket.send_json({"type": "error", "text": f"Недопустимый ход: {e}"})

            # ── Сброс игры ────────────────────────────
            elif msg_type == "reset":
                if color in ("white", "black"):
                    room.board.reset()
                    await room.broadcast({
                        "type": "update",
                        "board": room.get_board_array(),
                        "turn": room.whose_turn(),
                        "last_move": None,
                        "status": "reset",
                    })
                    sys_msg = {
                        "type": "chat",
                        "sender": "🎲 Система",
                        "text": f"{player_name} начал новую игру",
                        "system": True,
                    }
                    room.chat_history.append(sys_msg)
                    await room.broadcast(sys_msg)

    except WebSocketDisconnect:
        room.remove_player(websocket)
        leave_msg = {
            "type": "chat",
            "sender": "🎲 Система",
            "text": f"{player_name} покинул комнату",
            "system": True,
        }
        room.chat_history.append(leave_msg)
        await room.broadcast(leave_msg)
        logger.info(f"[{room_id}] {player_name} отключился")
    except Exception as e:
        logger.error(f"[{room_id}] Ошибка для {player_name}: {e}")
        room.remove_player(websocket)