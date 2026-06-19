from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
import chess
import threading
import time
import urllib.request
import os
import http.client
import json
from html_templates import get_game_html

app = FastAPI()

# Хранилище комнат. Структура:
# rooms[room_id] = {
#    "white_ws": WebSocket or None,
#    "black_ws": WebSocket or None,
#    "engine_board": chess.Board(),
#    "spectators": []
# }
rooms = {}

@app.get("/")
async def get_home():
    return HTMLResponse("<h1>Шакал-Шахматы запущены!</h1><p>Перейдите в комнату <a href='/game/777'>/game/777</a></p>")

@app.get("/game/{room_id}")
async def get_room(room_id: str):
    return HTMLResponse(get_game_html(room_id))

def get_board_matrix(board: chess.Board):
    matrix = []
    for r in reversed(range(8)):
        row = []
        for c in range(8):
            piece = board.piece_at(chess.square(c, r))
            if piece is None:
                row.append(".")
            else:
                row.append(piece.symbol())
    return matrix

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    
    # Если комнаты нет — создаем с нуля
    if room_id not in rooms:
        rooms[room_id] = {
            "white_ws": None,
            "black_ws": None,
            "engine_board": chess.Board(),
            "spectators": []
        }
        
    room = rooms[room_id]
    
    # Жесткое распределение ролей (занимаем свободные места игроками)
    if room["white_ws"] is None:
        room["white_ws"] = websocket
        role = "white"
    elif room["black_ws"] is None:
        room["black_ws"] = websocket
        role = "black"
    else:
        room["spectators"].append(websocket)
        role = "spectator"
        
    current_turn = "white" if room["engine_board"].turn == chess.WHITE else "black"
    
    # Отправляем игроку его реальную роль и состояние доски
    await websocket.send_json({
        "type": "init", 
        "role": role, 
        "board": get_board_matrix(room["engine_board"]), 
        "turn": current_turn
    })
    
    # Оповещаем чат о новом подключении
    rus_role = "Белые" if role == "white" else "Чёрные" if role == "black" else "Зритель"
    await broadcast_to_room(room, {
        "type": "chat",
        "sender": "📢 Системный Бот",
        "text": f"В игру зашел {rus_role}!"
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "move":
                # Ходить может только тот, чей сейчас ход на сервере
                current_turn = "white" if room["engine_board"].turn == chess.WHITE else "black"
                if role != current_turn:
                    continue

                old_matrix = get_board_matrix(room["engine_board"])
                new_matrix = data["board"]
                
                # Вычисляем, откуда и куда передвинули фигуру
                from_sq = None
                to_sq = None
                
                for r in range(8):
                    for c in range(8):
                        if old_matrix[r][c] != "." and new_matrix[r][c] == ".":
                            from_sq = chess.square(c, 7 - r)
                        elif old_matrix[r][c] != new_matrix[r][c] and new_matrix[r][c] != ".":
                            to_sq = chess.square(c, 7 - r)

                if from_sq is not None and to_sq is not None:
                    move = chess.Move(from_sq, to_sq)
                    piece = room["engine_board"].piece_at(from_sq)
                    
                    # Проверка на превращение пешки в Ферзя
                    if piece and piece.piece_type == chess.PAWN and chess.square_rank(to_sq) in [0, 7]:
                        move.promotion = chess.QUEEN

                    # Проверяем ход на легальность по правилам шахмат
                    if move in room["engine_board"].legal_moves:
                        room["engine_board"].push(move)
                        next_turn = "white" if room["engine_board"].turn == chess.WHITE else "black"
                        
                        # Рассылаем всем игрокам обновленную доску
                        await broadcast_to_room(room, {
                            "type": "update", 
                            "board": get_board_matrix(room["engine_board"]), 
                            "turn": next_turn
                        })
                    else:
                        # Если ход нелегальный — принудительно возвращаем игроку старую доску
                        await websocket.send_json({
                            "type": "update", 
                            "board": get_board_matrix(room["engine_board"]), 
                            "turn": current_turn
                        })
                    
            elif data["type"] == "chat":
                await broadcast_to_room(room, {
                    "type": "chat", 
                    "sender": data["sender"], 
                    "text": data["text"]
                })
                    
    except WebSocketDisconnect:
        # Если игрок отключился или обновил страницу — освобождаем конкретно ЕГО место
        if role == "white":
            room["white_ws"] = None
        elif role == "black":
            room["black_ws"] = None
        elif websocket in room["spectators"]:
            room["spectators"].remove(websocket)
            
        # Если в комнате вообще никого не осталось — удаляем комнату
        if room["white_ws"] is None and room["black_ws"] is None and len(room["spectators"]) == 0:
            if room_id in rooms:
                del rooms[room_id]
        else:
            await broadcast_to_room(room, {
                "type": "chat",
                "sender": "📢 Системный Бот",
                "text": f"{rus_role} покинул игру или обновил страницу."
            })

async def broadcast_to_room(room, message):
    """Вспомогательная функция для отправки сообщений всем участникам комнаты"""
    targets = []
    if room["white_ws"]: targets.append(room["white_ws"])
    if room["black_ws"]: targets.append(room["black_ws"])
    for spec in room["spectators"]:
        targets.append(spec)
        
    for ws in targets:
        try:
            await ws.send_json(message)
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)