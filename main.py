
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import threading
import time
import urllib.request
from html_templates import get_game_html

app = FastAPI()

rooms = {}

def keep_alive(app_url):
    while True:
        time.sleep(600)
        try:
            urllib.request.urlopen(app_url)
            print("🌸 Пинг хостинга выполнен успешно! Сервер не спит.")
        except Exception as e:
            print(f"⚠️ Ошибка пинга: {e}")

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
            "turn": "white",  # Кто сейчас ходит
            "board": [
                ["R", "N", "B", "Q", "K", "B", "N", "R"],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                [".", ".", ".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", ".", ".", "."],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                ["r", "n", "b", "q", "k", "b", "n", "r"]
            ]
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
        
    await websocket.send_json({"type": "init", "role": role, "board": room["board"], "turn": room["turn"]})
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "move" and role == room["turn"]:
                room["board"] = data["board"]
                # Меняем ход на противоположный после успешного движения
                room["turn"] = "black" if room["turn"] == "white" else "white"
                
                for conn in room["connections"]:
                    await conn.send_json({"type": "update", "board": room["board"], "turn": room["turn"]})
                    
            elif data["type"] == "chat":
                for conn in room["connections"]:
                    await conn.send_json({"type": "chat", "sender": data["sender"], "text": data["text"]})
                    
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