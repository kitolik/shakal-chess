def get_game_html(room_id: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Шахматы</title>
        <style>
            body {{ background: #1a1a1a; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
            .board {{ display: grid; grid-template-columns: repeat(8, 60px); grid-template-rows: repeat(8, 60px); border: 5px solid #333; }}
            .sq {{ width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; font-size: 40px; cursor: pointer; }}
            .w {{ background: #f0d9b5; color: black; }}
            .b {{ background: #b58863; color: black; }}
            .chat {{ width: 300px; height: 480px; background: #222; border: 1px solid #444; display: flex; flex-direction: column; }}
            #msgs {{ flex: 1; overflow-y: auto; padding: 10px; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div id="role-text" style="margin-bottom:10px; font-weight:bold;">Загрузка...</div>
        <div style="display:flex; gap:20px;">
            <div class="board" id="chessboard"></div>
            <div class="chat">
                <div id="msgs"></div>
                <div style="display:flex; padding:5px;">
                    <input type="text" id="inp" style="flex:1;">
                    <button onclick="sendMsg()">Ок</button>
                </div>
            </div>
        </div>

        <script>
            let myRole = "";
            const ws = new WebSocket("ws://" + window.location.host + "/ws/{room_id}");

            ws.onmessage = (e) => {{
                const d = JSON.parse(e.data);
                if (d.type === "init") {{
                    myRole = d.role;
                    document.getElementById("role-text").innerText = "Вы: " + (myRole === "white" ? "Белые" : "Чёрные");
                    render(d.board);
                }} else if (d.type === "update") {{
                    render(d.board);
                }} else if (d.type === "chat") {{
                    const m = document.getElementById("msgs");
                    m.innerHTML += "<div><b>" + d.sender + ":</b> " + d.text + "</div>";
                    m.scrollTop = m.scrollHeight;
                }}
            }};

            function render(board) {{
                const b = document.getElementById("chessboard");
                b.innerHTML = "";
                for (let r = 0; r < 8; r++) {{
                    for (let c = 0; c < 8; c++) {{
                        const sq = document.createElement("div");
                        sq.className = "sq " + ((r + c) % 2 === 0 ? "w" : "b");
                        sq.innerText = board[r][c] === "." ? "" : board[r][c];
                        sq.onclick = () => {{ /* тут логика хода */ }};
                        b.appendChild(sq);
                    }}
                }}
            }}

            function sendMsg() {{
                const i = document.getElementById("inp");
                ws.send(JSON.stringify({{type: "chat", sender: myRole, text: i.value}}));
                i.value = "";
            }}
        </script>
    </body>
    </html>
    """