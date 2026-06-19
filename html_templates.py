def get_game_html(room_id: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Шакал-Шахматы — Комната {room_id}</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                /* Заменяем тяжелую картинку на крутой быстрый космический градиент */
                background: radial-gradient(circle at top right, #1e102f, #0b0813);
                color: #fff;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                overflow: hidden;
            }}
            
            .status-box {{
                background: rgba(20, 16, 35, 0.85);
                padding: 12px 25px;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 20px;
                border: 2px solid #a970ff;
                box-shadow: 0 0 20px rgba(169, 112, 255, 0.4);
                backdrop-filter: blur(8px);
            }}
            
            .game-container {{
                display: flex;
                gap: 25px;
                align-items: flex-start;
                background: rgba(15, 12, 28, 0.85);
                padding: 20px;
                border-radius: 16px;
                box-shadow: 0 20px 50px rgba(0,0,0,0.7);
                border: 1px solid rgba(169, 112, 255, 0.2);
                backdrop-filter: blur(8px);
            }}
            
            .board {{
                display: grid;
                grid-template-columns: repeat(8, 65px);
                grid-template-rows: repeat(8, 65px);
                border: 6px solid #28233b;
                border-radius: 8px;
                box-shadow: 0 5px 25px rgba(0,0,0,0.5);
            }}
            
            .square {{
                width: 65px;
                height: 65px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 48px;
                cursor: pointer;
                user-select: none;
                transition: background-color 0.1s;
            }}
            
            /* Цвета доски: делаем их более контрастными для глаз */
            .white-sq {{ background-color: #f0d9b5; }}
            .black-sq {{ background-color: #b58863; }}
            
            /* Стилизация фигур, чтобы они четко отличались */
            .piece-white {{
                color: #ffffff;
                text-shadow: 
                    1px 1px 2px #000, 
                   -1px -1px 2px #000, 
                    1px -1px 2px #000, 
                   -1px 1px 2px #000,
                    0px 0px 4px rgba(0,0,0,0.8);
            }}
            
            .piece-black {{
                color: #1a1a1a;
                text-shadow: 
                    1px 1px 1px #fff,
                   -1px -1px 1px #fff,
                    1px -1px 1px #fff,
                   -1px 1px 1px #fff;
            }}
            
            .selected {{ 
                background-color: #7bdcb5 !important;
                box-shadow: inset 0 0 15px rgba(0,0,0,0.4);
            }}
            
            .side-panel {{
                display: flex;
                flex-direction: column;
                gap: 15px;
            }}
            
            .chat-container {{
                width: 300px;
                height: 380px;
                background-color: #0e0c15;
                border: 2px solid #231f38;
                border-radius: 12px;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }}
            
            .chat-title {{
                background: linear-gradient(90deg, #9146ff, #6441a5);
                padding: 12px;
                text-align: center;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 1px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            }}
            
            .messages {{
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                font-size: 14px;
                display: flex;
                flex-direction: column;
                gap: 8px;
            }}
            
            .messages div {{
                background: rgba(255,255,255,0.03);
                padding: 8px 12px;
                border-radius: 8px;
                border-left: 3px solid #9146ff;
            }}
            
            .input-area {{
                display: flex;
                padding: 12px;
                gap: 8px;
                border-top: 1px solid #231f38;
                background: #13111c;
            }}
            
            .input-area input {{
                flex: 1;
                background: #09080e;
                border: 1px solid #383254;
                color: #fff;
                padding: 10px;
                border-radius: 6px;
                outline: none;
            }}
            
            .input-area button {{
                background: #9146ff;
                border: none;
                color: white;
                padding: 8px 18px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: bold;
                transition: background 0.2s;
            }}
            .input-area button:hover {{ background: #772ce8; }}
            
            .controls-panel {{
                display: flex;
                gap: 10px;
            }}
            
            .btn {{
                flex: 1;
                padding: 12px;
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                cursor: pointer;
                font-size: 14px;
                transition: transform 0.1s, opacity 0.2s;
            }}
            .btn:active {{ transform: scale(0.96); }}
            .btn:hover {{ opacity: 0.9; }}
            .btn-resign {{ background: #eb0400; }}
            .btn-draw {{ background: #3a3b45; }}
            
            .modal {{
                display: none;
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.8);
                z-index: 100;
                align-items: center;
                justify-content: center;
                backdrop-filter: blur(4px);
            }}
            
            .modal-content {{
                background: #181623;
                border: 2px solid #9146ff;
                padding: 30px;
                border-radius: 16px;
                text-align: center;
            }}
            
            .modal-buttons {{
                display: flex;
                gap: 15px;
                margin-top: 20px;
                justify-content: center;
            }}
            
            .modal-btn {{
                padding: 10px 25px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
            }}
            .btn-accept {{ background: #00b589; color: white; }}
            .btn-decline {{ background: #eb0400; color: white; }}
        </style>
    </head>
    <body>

        <div class="status-box" id="role-status">Загрузка комнаты...</div>

        <div class="game-container">
            <div class="board" id="chessboard"></div>

            <div class="side-panel">
                <div class="chat-container">
                    <div class="chat-title">💬 ТВИЧ-ЧАТ МАТЧА</div>
                    <div class="messages" id="chat-messages"></div>
                    <div class="input-area">
                        <input type="text" id="chat-input" placeholder="Написать в чат...">
                        <button id="send-btn">Ок</button>
                    </div>
                </div>
                
                <div class="controls-panel">
                    <button class="btn btn-resign" id="resign-btn">🏳️ Сдаться</button>
                    <button class="btn btn-draw" id="draw-btn">🤝 Ничья</button>
                </div>
            </div>
        </div>

        <div class="modal" id="draw-modal">
            <div class="modal-content">
                <h3>🤝 Соперник предлагает ничью!</h3>
                <div class="modal-buttons">
                    <button class="modal-btn btn-accept" id="draw-accept">Принять</button>
                    <button class="modal-btn btn-decline" id="draw-decline">Отклонить</button>
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

            // Используем заполненные юникод-фигуры для лучшего рендеринга стилей
            const unicodePieces = {{
                'P': '♟', 'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚',
                'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
                '.': ''
            }};

            function updateStatusText() {{
                const turnText = currentTurn === "white" ? "Ход: Белых" : "Ход: Чёрных";
                let roleText = "👀 Зритель";
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
                        if (piece && piece !== '.') {{
                            square.innerText = unicodePieces[piece];
                            // Добавляем класс цвета в зависимости от регистра (ЗАГЛАВНЫЕ = белые)
                            if (piece === piece.toUpperCase()) {{
                                square.classList.add("piece-white");
                            }} else {{
                                square.classList.add("piece-black");
                            }}
                        }}
                        
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
                const isWhitePiece = (piece === piece.toUpperCase());
                return (myRole === "white" && isWhitePiece) || (myRole === "black" && !isWhitePiece);
            }}

            function handleSquareClick(r, c) {{
                if (myRole === "spectator" || myRole !== currentTurn) return;
                
                const clickedPiece = boardState[r][c];
                
                if (selectedSquare) {{
                    if (isYourPiece(clickedPiece)) {{
                        selectedSquare = {{ row: r, col: c }};
                        drawBoard();
                        return;
                    }}
                    
                    let nextBoard = JSON.parse(JSON.stringify(boardState));
                    const movingPiece = nextBoard[selectedSquare.row][selectedSquare.col];
                    nextBoard[r][c] = movingPiece;
                    nextBoard[selectedSquare.row][selectedSquare.col] = ".";
                    
                    ws.send(JSON.stringify({{ "type": "move", "board": nextBoard }}));
                    selectedSquare = null;
                }} else {{
                    if (isYourPiece(clickedPiece)) {{
                        selectedSquare = {{ row: r, col: c }};
                    }}
                }}
                drawBoard();
            }}

            ws.onmessage = (event) => {{
                const data = JSON.parse(event.data);
                
                if (data.type === "init" || data.type === "update") {{
                    if (data.type === "init") myRole = data.role;
                    boardState = data.board;
                    currentTurn = data.turn;
                    updateStatusText();
                    drawBoard();
                }} else if (data.type === "chat") {{
                    const msgDiv = document.createElement("div");
                    msgDiv.innerHTML = "<b>" + data.sender + ":</b> " + data.text;
                    const container = document.getElementById("chat-messages");
                    container.appendChild(msgDiv);
                    container.scrollTop = container.scrollHeight;
                }} else if (data.type === "system_alert") {{
                    const msgDiv = document.createElement("div");
                    msgDiv.innerHTML = "<span style='color: #ff4a8d; font-weight:bold;'>📢 " + data.text + "</span>";
                    document.getElementById("chat-messages").appendChild(msgDiv);
                }} else if (data.type === "draw_offer" && data.from !== myRole) {{
                    document.getElementById("draw-modal").style.display = "flex";
                }} else if (data.type === "draw_close") {{
                    document.getElementById("draw-modal").style.display = "none";
                }}
            }};

            function sendChatMessage() {{
                const input = document.getElementById("chat-input");
                if (input.value.trim() !== "") {{
                    let name = "👀 Зритель";
                    if (myRole === "white") name = "⚪ Белый";
                    if (myRole === "black") name = "⚫ Чёрный";
                    ws.send(JSON.stringify({{ "type": "chat", "sender": name, "text": input.value }}));
                    input.value = "";
                }}
            }}

            document.getElementById("resign-btn").onclick = () => {{
                if (myRole === "spectator") return;
                if (confirm("Вы уверены, что хотите сдаться?")) {{
                    ws.send(JSON.stringify({{ "type": "resign", "player": myRole }}));
                }}
            }};

            document.getElementById("draw-btn").onclick = () => {{
                if (myRole === "spectator") return;
                ws.send(JSON.stringify({{ "type": "draw_offer", "player": myRole }}));
            }};

            document.getElementById("draw-accept").onclick = () => {{
                ws.send(JSON.stringify({{ "type": "draw_respond", "accepted": true }}));
            }};

            document.getElementById("draw-decline").onclick = () => {{
                ws.send(JSON.stringify({{ "type": "draw_respond", "accepted": false }}));
            }};

            document.getElementById("send-btn").onclick = sendChatMessage;
            document.getElementById("chat-input").onkeydown = (e) => {{ if (e.key === 'Enter') sendChatMessage(); }};
        </script>
    </body>
    </html>
    """