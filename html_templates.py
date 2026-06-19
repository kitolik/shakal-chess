def get_game_html(room_id: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Шакал-Шахматы — Комната {room_id}</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: sans-serif;
                background-color: #1e1e24;
                color: #fff;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            .status-box {{
                background-color: #2a2a35;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 15px;
                border: 1px solid #ff4a8d;
            }}
            .game-container {{
                display: flex;
                gap: 20px;
                align-items: flex-start;
            }}
            .board {{
                display: grid;
                grid-template-columns: repeat(8, 60px);
                grid-template-rows: repeat(8, 60px);
                border: 4px solid #333;
                border-radius: 4px;
            }}
            .square {{
                width: 60px;
                height: 60px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 42px;
                cursor: pointer;
                user-select: none;
            }}
            .white-sq {{ background-color: #eedcbf; color: #000; }}
            .black-sq {{ background-color: #b88b64; color: #000; }}
            .selected {{ background-color: #fffa73 !important; }}
            
            .chat-container {{
                width: 250px;
                height: 488px;
                background-color: #16161a;
                border: 2px solid #333;
                border-radius: 4px;
                display: flex;
                flex-direction: column;
            }}
            .chat-title {{
                background-color: #24242b;
                padding: 10px;
                text-align: center;
                font-size: 14px;
                font-weight: bold;
                border-bottom: 1px solid #333;
            }}
            .messages {{
                flex: 1;
                padding: 10px;
                overflow-y: auto;
                font-size: 14px;
                display: flex;
                flex-direction: column;
                gap: 5px;
            }}
            .input-area {{
                display: flex;
                padding: 10px;
                gap: 5px;
                border-top: 1px solid #333;
            }}
            .input-area input {{
                flex: 1;
                background: #24242b;
                border: 1px solid #444;
                color: #fff;
                padding: 5px;
                border-radius: 3px;
            }}
            .input-area button {{
                background-color: #ff4a8d;
                border: none;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                cursor: pointer;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>

        <div class="status-box" id="role-status">Подключение к серверу...</div>

        <div class="game-container">
            <div class="board" id="chessboard"></div>

            <div class="chat-container">
                <div class="chat-title">ТВИЧ-ЧАТ МАТЧА</div>
                <div class="messages" id="chat-messages"></div>
                <div class="input-area">
                    <input type="text" id="chat-input" placeholder="Отправить сообщение...">
                    <button id="send-btn">Ок</button>
                </div>
            </div>
        </div>

        <script>
            const roomId = "{room_id}";
            // Автоматически переключаем протокол ws:// или wss:// в зависимости от хостинга
            const wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
            const ws = new WebSocket(wsProtocol + window.location.host + "/ws/" + roomId);

            let myRole = "spectator";
            let boardState = [];
            let selectedSquare = null;

            // Карта Юникод-фигур
            const unicodePieces = {{
                'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚', 'P': '♟',
                'r': '♖', 'n': '♘', 'b': '♗', 'q': '♕', 'k': '♔', 'p': '♙',
                '.': ''
            }};

            const roleNames = {{
                'white': 'Вы: ⚪ Белые | Ход: Белых',
                'black': 'Вы: ⚫ Чёрные | Ход: Белых',
                'spectator': 'Вы: 👀 Зритель | Ход: Белых'
            }};

            function drawBoard() {{
                const boardDiv = document.getElementById("chessboard");
                boardDiv.innerHTML = "";
                
                for (let r = 0; r < 8; r++) {{
                    for (let c = 0; c < 8; c++) {{
                        const square = document.createElement("div");
                        const isBlackType = (r + c) % 2 === 1;
                        square.className = "square " + (isBlackType ? "black-sq" : "white-sq");
                        square.dataset.row = r;
                        square.dataset.col = c;
                        
                        const piece = boardState[r][c];
                        square.innerText = unicodePieces[piece] || "";
                        
                        if (selectedSquare && selectedSquare.row === r && selectedSquare.col === c) {{
                            square.classList.add("selected");
                        }}
                        
                        square.onclick = () => handleSquareClick(r, c);
                        boardDiv.appendChild(square);
                    }}
                }}
            }}

            function handleSquareClick(r, c) {{
                if (myRole === "spectator") return;
                
                if (selectedSquare) {{
                    const p = boardState[selectedSquare.row][selectedSquare.col];
                    boardState[c][selectedSquare.col] = "."; // Простейшая логика перемещения без правил шахмат
                    boardState[r][c] = p;
                    boardState[selectedSquare.row][selectedSquare.col] = ".";
                    
                    ws.send(JSON.stringify({{ "type": "move", "board": boardState }}));
                    selectedSquare = null;
                }} else {{
                    if (boardState[r][c] !== ".") {{
                        selectedSquare = {{ row: r, col: c }};
                    }}
                }}
                drawBoard();
            }}

            ws.onmessage = (event) => {{
                const data = JSON.parse(event.data);
                
                if (data.type === "init") {{
                    myRole = data.role;
                    boardState = data.board;
                    document.getElementById("role-status").innerText = roleNames[myRole];
                    drawBoard();
                }} else if (data.type === "update") {{
                    boardState = data.board;
                    drawBoard();
                }} else if (data.type === "chat") {{
                    const msgDiv = document.createElement("div");
                    msgDiv.innerHTML = `<b>$ {{data.sender}}:</b> $ {{data.text}}`;
                    document.getElementById("chat-messages").appendChild(msgDiv);
                }}
            }};

            // Логика чата
            function sendChatMessage() {{
                const input = document.getElementById("chat-input");
                if (input.value.trim() !== "") {{
                    let name = myRole === "white" ? "Белый" : (myRole === "black" ? "Чёрный" : "Зритель");
                    ws.send(JSON.stringify({{
                        "type": "chat",
                        "sender": name,
                        "text": input.value
                    }}));
                    input.value = "";
                }}
            }}

            document.getElementById("send-btn").onclick = sendChatMessage;
            document.getElementById("chat-input").onkeydown = (e) => {{ if (e.key === 'Enter') sendChatMessage(); }};
        </script>
    </body>
    </html>
    """