from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
import chess
import threading
import time
import urllib.request
import os
from html_templates import get_game_html

app = FastAPI()

rooms = {}

# Раздаём фоновую картинку прямо из корня проекта
@app.get("/bg.jpg")
async def get_background():
    if os.path.exists("bg.jpg"):
        return FileResponse("bg.jpg")
    return HTMLResponse("Background not found", status_code=404)

def keep_alive(app_url):
    while True:
        time.sleep(600)
        try:
            urllib.request.urlopen(app_url)
            print("🌸 Пинг хостинга выполнен успешно!")
        except Exception as e:
            print(f"⚠️ Ошибка пинга: {e}")

# Конвертация доски python-chess в матрицу для фронтенда
def get_board_matrix(board: chess.Board):
    matrix = []
    for r in reversed(range(8)):
        row = []
        for c in range(8):
            piece = board.piece_at(chess.square(c, r))
            if piece is None:
                row.append(".")
            else:
                # python-chess: заглавные — белые, строчные — черные.
                # Инвертируем регистр для правильного отображения Юникод-фигур на фронте
                symbol = piece.symbol()
                row.append(symbol.lower() if piece.color == chess.WHITE else symbol.upper())
        matrix.append(row)
    return matrix

@app.get("/")
async def get_home():
    return HTMLResponse("<h1>Шакал-Шахматы запущены!</h1><p>Перейдите в комнату <a href='/game/777'>/game/777</a></p>")

@app.get("/game/{room_id}")
async def get_room(room_id: str):
    return HTMLResponse(get_game_html(room_id))

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    
    if room_id not in rooms:
        rooms[room_id] = {
            "connections": [],
            "white": None,
            "black": None,
            "engine_board": chess.Board(),
            "game_over": False
        }
        
    room = rooms[room_id]
    room["connections"].append(websocket)
    
    if room["white"] is None:
        room["white"] = websocket
        role = "white"
    elif room["black"] is None:
        room["black"] = websocket
        role = "black"
    else:
        role = "spectator"
        
    current_turn = "white" if room["engine_board"].turn == chess.WHITE else "black"
    await websocket.send_json({
        "type": "init", 
        "role": role, 
        "board": get_board_matrix(room["engine_board"]), 
        "turn": current_turn
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if room["game_over"] and data["type"] in ["move", "resign", "draw_offer"]:
                continue

            if data["type"] == "move":
                current_turn = "white" if room["engine_board"].turn == chess.WHITE else "black"
                if role != current_turn:
                    continue

                old_matrix = get_board_matrix(room["engine_board"])
                new_matrix = data["board"]
                
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
                    
                    # Авто-превращение пешки в ферзя на последней горизонтали
                    piece = room["engine_board"].piece_at(from_sq)
                    if piece and piece.piece_type == chess.PAWN and chess.square_rank(to_sq) in [0, 7]:
                        move.promotion = chess.QUEEN

                    # Проверка хода шахматным движком
                    if move in room["engine_board"].legal_moves:
                        room["engine_board"].push(move)
                        next_turn = "white" if room["engine_board"].turn == chess.WHITE else "black"
                        
                        status_alert = None
                        if room["engine_board"].is_checkmate():
                            room["game_over"] = True
                            status_alert = f"Мат! Игра окончена. Победили {'Чёрные' if next_turn == 'white' else 'Белые'}!"
                        elif room["engine_board"].is_stalemate():
                            room["game_over"] = True
                            status_alert = "Ничья (Пат)!"
                        elif room["engine_board"].is_check():
                            status_alert = "⚠️ Шах!"

                        for conn in room["connections"]:
                            await conn.send_json({
                                "type": "update", 
                                "board": get_board_matrix(room["engine_board"]), 
                                "turn": next_turn
                            })
                            if status_alert:
                                await conn.send_json({"type": "system_alert", "text": status_alert})
                    else:
                        # Откат нелегального хода (защита от телепортации)
                        await websocket.send_json({
                            "type": "update", 
                            "board": get_board_matrix(room["engine_board"]), 
                            "turn": current_turn
                        })
                        await websocket.send_json({"type": "system_alert", "text": "❌ Этот ход нарушает правила шахмат!"})
                    
            elif data["type"] == "chat":
                for conn in room["connections"]:
                    await conn.send_json({"type": "chat", "sender": data["sender"], "text": data["text"]})

            elif data["type"] == "resign":
                room["game_over"] = True
                loser = "Белые" if data["player"] == "white" else "Чёрные"
                winner = "Чёрные" if data["player"] == "white" else "Белые"
                for conn in room["connections"]:
                    await conn.send_json({"type": "system_alert", "text": f"Матч окончен! {loser} сдались. Победа {winner}!"})

            elif data["type"] == "draw_offer":
                for conn in room["connections"]:
                    await conn.send_json({"type": "draw_offer", "from": data["player"]})
                    
            elif data["type"] == "draw_respond":
                for conn in room["connections"]:
                    await conn.send_json({"type": "draw_close"})
                if data["accepted"]:
                    room["game_over"] = True
                    for conn in room["connections"]:
                        await conn.send_json({"type": "system_alert", "text": "🤝 Ничья принята! Игра завершена."})
                    
    except WebSocketDisconnect:
        room["connections"].remove(websocket)
        if room["white"] == websocket:
            room["white"] = None
        elif room["black"] == websocket:
            room["black"] = None
            
        if len(room["connections"]) == 0:
            del rooms[room_id]

if __name__ == "__main__":
    PORT = 8000
    RENDER_APP_URL = "https://shakal-chess.onrender.com/"
    ping_thread = threading.Thread(target=keep_alive, args=(RENDER_APP_URL,), daemon=True)
    ping_thread.start()
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")