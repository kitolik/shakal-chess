def get_game_html(room_id: str) -> str:
    # Используем двойные фигурные скобки {{}} для CSS/JS, чтобы Python f-строка их не ломала,
    # а для JS-переменных внутри строк используем обычные кавычки и плюсы.
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
            const wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
            const ws = new WebSocket(wsProtocol + window.location.host + "/ws/" + roomId);

            let myRole = "spectator";
            let currentTurn = "white";
            let boardState = [];
            let selectedSquare = null;

            const unicodePieces = {{
                'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚', 'P': '♟',
                'r': '♖', 'n': '♘', 'b': '♗', 'q': '♕', 'k': '♔', 'p': '♙',
                '.': ''
            }};

            function updateStatusText() {{
                const turnText = currentTurn === "white" ? "Ход: Белых" : "Ход: Чёрных";
                let roleText = "Зритель";
                if (myRole === "white") roleText = "⚪ Белые";
                if (myRole === "black") roleText = "⚫ Чёрные";
                
                document.getElementById("role-status").innerText = "Вы: " + roleText + " | " + turnText;
            }}

            function drawBoard() {{
                const boardDiv = document.getElementById("chessboard");
                boardDiv.innerHTML = "";
                
                for (let r = 0; r < 8; r++) {{
                    for (let c = 0; c < 8; c++) {{
                        const square = document.createElement("div");
                        const isBlackType = (r + c) % 2 === 1;
                        square.className = "square " + (isBlackType ? "black-sq" : "white-sq");
                        
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

            function isYourPiece(piece) {{
                if (!piece || piece === '.') return false;
                const isWhitePiece = piece === piece.toLowerCase();
                return (myRole === "white" && isWhitePiece) || (myRole === "black" && !isWhitePiece);
            }}

            function handleSquareClick(r, c) {{
                if (myRole === "spectator" || myRole !== currentTurn) return;
                
                const clickedPiece = boardState[r][c];
                
                if (selectedSquare) {{
                    // Если кликнули на другую свою фигуру — перевыбираем её
                    if (isYourPiece(clickedPiece)) {{
                        selectedSquare = {{ row: r, col: c }};
                        drawBoard();
                        return;
                    }}
                    
                    // Сама логика перемещения (пока без строгих шахматных правил, но ходить можно)
                    const movingPiece = boardState[selectedSquare.row][selectedSquare.col];
                    boardState[r][c] = movingPiece;
                    boardState[selectedSquare.row][selectedSquare.col] = ".";
                    
                    ws.send(JSON.stringify({{ "type": "move", "board": boardState }}));
                    selectedSquare = null;
                }} else {{
                    // Выбираем фигуру только если она принадлежит текущему игроку
                    if (isYourPiece(clickedPiece)) {{
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
                    currentTurn = data.turn;
                    updateStatusText();
                    drawBoard();
                }} else if (data.type === "update") {{
                    boardState = data.board;
                    currentTurn = data.turn;
                    updateStatusText();
                    drawBoard();
                }} else if (data.type === "chat") {{
                    const msgDiv = document.createElement("div");
                    // Исправлено: чистый JS без поломки от f-строки Python
                    msgDiv.innerHTML = "<b>" + data.sender + ":</b> " + data.text;
                    const messagesContainer = document.getElementById("chat-messages");
                    messagesContainer.appendChild(msgDiv);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }}
            }};

            function sendChatMessage() {{
                const input = document.getElementById("chat-input");
                if (input.value.trim() !== "") {{
                    let name = "Зритель";
                    if (myRole === "white") name = "Белый";
                    if (myRole === "black") name = "Чёрный";
                    
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