
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import random
import subprocess
import threading
import time
import re

# Импортируем твой HTML шаблон из соседнего файла
from html_templates import HTML_TEMPLATE

app = FastAPI()
games = {}

@app.get("/")
async def get_index():
    game_id = str(random.randint(100000000, 999999999))
    return HTMLResponse(f'<h2>Комната создана! Отправь другу ссылку:</h2><a href="/game/{game_id}">Войти в игру</a>')

@app.get("/game/{game_id}")
async def get_game(game_id: str):
    return HTMLResponse(HTML_TEMPLATE)

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()
    
    if game_id not in games:
        games[game_id] = {
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "white": None,
            "black": None,
            "connections": []
        }
    
    game = games[game_id]
    game["connections"].append(websocket)
    
    # Автоматическое распределение ролей
    if game["white"] is None:
        role = "white"
        game["white"] = websocket
    elif game["black"] is None:
        role = "black"
        game["black"] = websocket
    else:
        role = "spectator"
        
    await websocket.send_json({"type": "init", "role": role, "fen": game["fen"]})
    
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "move":
                game["fen"] = data["move"]
                for conn in game["connections"]:
                    if conn != websocket:
                        await conn.send_json({"type": "update", "fen": game["fen"]})
            elif data["type"] == "chat":
                for conn in game["connections"]:
                    await conn.send_json({"type": "chat", "senderRole": role, "text": data["text"]})
    except WebSocketDisconnect:
        game["connections"].remove(websocket)
        if game["white"] == websocket: game["white"] = None
        if game["black"] == websocket: game["black"] = None


# Функция для автоматического запуска фонового интернет-туннеля
def start_tunnel(port, game_id):
    print("🌸 Создаю автоматическую ссылку для Дискорда через Ngrok...")
    from pyngrok import ngrok, conf
    import logging
    
    # Отключаем лишний спам библиотеки в консоль
    logging.getLogger("pyngrok").setLevel(logging.WARNING)
    
    try:
        # !!! КРИТИЧЕСКИ ВАЖНО: Вставь свой токен с сайта между кавычек ниже !!!
        MY_TOKEN = "3FKAYw8fGFs2ctYmj8RcKYmjmpI_5ZEtJ2YgEhWn226H6JDLo"
        
        config = conf.PyngrokConfig(auth_token=MY_TOKEN)
        
        # Поднимаем стабильный туннель
        tunnel = ngrok.connect(port, pyngrok_config=config)
        public_url = tunnel.public_url
        
        # Переводим на безопасный протокол https
        if public_url.startswith("http://"):
            public_url = public_url.replace("http://", "https://")
            
        print("\n" + "="*70)
        print("  🎉 ВСЁ ГОТОВО! ССЫЛКА ДЛЯ ДИСКОРДА (ОТПРАВЬ ДРУГУ):")
        print(f"  {public_url}/game/{game_id}")
        print("="*70 + "\n")
    except Exception as e:
        print(f"⚠️ Ошибка создания ссылки ngrok: {e}")
        

if __name__ == "__main__":
    PORT = 8000
    start_game_id = str(random.randint(100000, 999999))
    
    # Запуск потока генерации ссылки
    tunnel_thread = threading.Thread(target=start_tunnel, args=(PORT, start_game_id), daemon=True)
    tunnel_thread.start()
    
    time.sleep(1)
    # Меняем 127.0.0.1 на 0.0.0.0, чтобы сервер слушал все входящие подключения от туннеля
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")