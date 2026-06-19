HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌸 Shakal Chess Room</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/chessboard-js/1.0.0/chessboard-1.0.0.min.css">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chessboard-js/1.0.0/chessboard-1.0.0.min.js"></script>
    <style>
        body { 
            background: linear-gradient(135deg, #1e1e24 0%, #2a2830 100%); 
            color: #f5f5f5; font-family: sans-serif; display: flex; 
            flex-direction: column; align-items: center; justify-content: center; 
            min-height: 100vh; margin: 0; padding: 10px;
        }
        .status-panel {
            background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px);
            padding: 12px 25px; border-radius: 12px; border: 1px solid rgba(255, 182, 193, 0.2);
            font-size: 1.2rem; font-weight: bold; text-align: center; margin-bottom: 20px;
        }
        .game-container { display: flex; flex-direction: row; gap: 20px; max-width: 95vw; flex-wrap: wrap; justify-content: center; }
        #board-wrapper { padding: 8px; background: #111; border-radius: 10px; box-shadow: 0 15px 40px rgba(0,0,0,0.6); }
        #myBoard { width: 440px; max-width: 90vw; }
        
        .chat-container {
            width: 300px; max-width: 90vw; height: 456px;
            background: #18181b; border-radius: 10px; border: 1px solid #2f2f35;
            display: flex; flex-direction: column; box-shadow: 0 15px 40px rgba(0,0,0,0.6);
        }
        .chat-header { padding: 10px; background: #0f0f11; border-bottom: 1px solid #2f2f35; font-weight: bold; font-size: 0.9rem; text-transform: uppercase; color: #adadb8; border-radius: 10px 10px 0 0; }
        .chat-messages { flex: 1; padding: 10px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; font-size: 0.9rem; }
        .chat-message { line-height: 1.4; word-break: break-word; }
        .chat-author-white { color: #ffffff; font-weight: bold; }
        .chat-author-black { color: #ff79c6; font-weight: bold; }
        .chat-author-spectator { color: #7289da; font-weight: bold; }
        
        .chat-input-area { padding: 10px; background: #0f0f11; border-top: 1px solid #2f2f35; display: flex; gap: 5px; border-radius: 0 0 10px 10px; }
        .chat-input { flex: 1; background: #26262c; border: 2px solid transparent; border-radius: 6px; color: white; padding: 8px; outline: none; }
        .chat-input:focus { border-color: #db7093; }
        .chat-btn { background: #db7093; border: none; color: white; padding: 0 15px; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .chat-btn:hover { background: #b05574; }
    </style>
</head>
<body>
    <div class="status-panel" id="status">🌸 Подключение к комнате...</div>
    <div class="game-container">
        <div id="board-wrapper"><div id="myBoard"></div></div>
        <div class="chat-container">
            <div class="chat-header">Твич-чат матча</div>
            <div class="chat-messages" id="chatMessages"></div>
            <div class="chat-input-area">
                <input type="text" class="chat-input" id="chatInput" placeholder="Отправить сообщение..." maxlength="150">
                <button class="chat-btn" id="sendBtn">Ок</button>
            </div>
        </div>
    </div>
    <script>
        const gameId = window.location.pathname.split('/').pop();
        const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const socket = new WebSocket(wsProtocol + window.location.host + '/ws/' + gameId);
        
        let board = null; 
        let game = new Chess(); 
        let playerRole = 'spectator'; 

        // Идеальные классические силуэты в векторе, зашитые прямо в JS
        function getSvgPiece(piece) {
            const colors = { 
                'w': { fill: '#ffffff', stroke: '#000000', shadow: 'rgba(0,0,0,0.4)' }, 
                'b': { fill: '#222222', stroke: '#ffffff', shadow: 'rgba(255,255,255,0.2)' } 
            };
            const pColor = piece.charAt(0);
            const pType = piece.charAt(1);
            const c = colors[pColor];
            
            let d = '';
            if (pType === 'P') { // Пешка
                d = '<circle cx="25" cy="16" r="6.5"/><path d="M18 38h14l-3-15h-8z"/><path d="M14 41h22v2H14z"/>';
            } else if (pType === 'R') { // Ладья
                d = '<path d="M14 14h4v4h3v-4h4v4h3v-4h4v10H14z"/><path d="M14 24h17v14H14z"/><path d="M11 40h23v3H11z"/>';
            } else if (pType === 'N') { // Конь
                d = '<path d="M33 39L30 25q3-5-2-10t-11 3q-4 4-2 9l-4 3v4l5-1h4l1 5z"/><path d="M12 40h22v3H12z"/>';
            } else if (pType === 'B') { // Слон
                d = '<circle cx="25" cy="14" r="2"/><path d="M25 17c-4 0-6 4-6 8c0 5 6 12 6 12s6-7 6-12c0-4-2-8-6-8z"/><path d="M14 39h22v3H14z"/>';
            } else if (pType === 'Q') { // Ферзь
                d = '<path d="M13 18l3 17h18l3-17l-5 8l-4-12l-4 12z"/><path d="M12 39h22v3H12z"/><circle cx="13" cy="16" r="1.5"/><circle cx="25" cy="11" r="1.5"/><circle cx="37" cy="16" r="1.5"/>';
            } else if (pType === 'K') { // Король
                d = '<path d="M24 8h2v3h3v2h-3v4h-2v-4h-3v-2h3z"/><path d="M15 22c-2 4 1 15 10 15s12-11 10-15z"/><path d="M12 39h22v3H12z"/>';
            }

            const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50" width="100%" height="100%"><g fill="${c.fill}" stroke="${c.stroke}" stroke-width="2" stroke-linejoin="round" style="filter: drop-shadow(0px 2px 3px ${c.shadow});">${d}</g></svg>`;
            return 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
        }

        function onDragStart (source, piece, position, orientation) {
            if (game.game_over()) return false;
            if (playerRole === 'spectator') return false;
            if (playerRole === 'white' && (game.turn() !== 'w' || piece.search(/^b/) !== -1)) return false;
            if (playerRole === 'black' && (game.turn() !== 'b' || piece.search(/^w/) !== -1)) return false;
        }

        function onDrop (source, target) {
            if (source === target) return;

            let move = game.move({ from: source, to: target, promotion: 'q' });
            if (move === null) {
                alert("❌ Данный ход недоступен по правилам шахмат! Попробуйте еще раз.");
                return 'snapback';
            }
            socket.send(JSON.stringify({ type: 'move', move: source + target }));
        }

        function onSnapEnd () { board.position(game.fen()); }
        
        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.type === 'init') {
                playerRole = data.role; 
                game.load(data.fen);
                
                board = Chessboard('myBoard', {
                    draggable: true, 
                    position: data.fen, 
                    pieceTheme: getSvgPiece,
                    orientation: playerRole === 'black' ? 'black' : 'white',
                    onDragStart: onDragStart, 
                    onDrop: onDrop, 
                    onSnapEnd: onSnapEnd
                });
                updateStatus();
            } 
            
            if (data.type === 'update') { 
                game.load(data.fen); 
                board.position(data.fen); 
                updateStatus(); 
            }
            
            if (data.type === 'chat') { 
                appendMessage(data.senderRole, data.text); 
            }
        };
        
        function appendMessage(senderRole, text) {
            const container = document.getElementById('chatMessages');
            const msgEl = document.createElement('div'); msgEl.className = 'chat-message';
            let roleTag = '👁️ Зритель';
            let nameClass = 'chat-author-spectator';
            
            if (senderRole === 'white') { roleTag = '⚪ Белые'; nameClass = 'chat-author-white'; }
            if (senderRole === 'black') { roleTag = '⚫ Черные'; nameClass = 'chat-author-black'; }
            
            msgEl.innerHTML = '<span class="' + nameClass + '">' + roleTag + ':</span> ' + text;
            container.appendChild(msgEl); 
            container.scrollTop = container.scrollHeight;
        }

        function sendChatMessage() {
            const input = document.getElementById('chatInput'); const text = input.value.trim();
            if (text.length > 0) { socket.send(JSON.stringify({ type: 'chat', text: text })); input.value = ''; }
        }

        document.getElementById('sendBtn').addEventListener('click', sendChatMessage);
        document.getElementById('chatInput').addEventListener('keypress', function(e) { if (e.key === 'Enter') sendChatMessage(); });
        
        function updateStatus() {
            let roleText = "Вы: 👀 Зритель";
            if (playerRole === 'white') roleText = "Вы: Игрок (Белые ⚪)";
            if (playerRole === 'black') roleText = "Вы: Игрок (Черные ⚫)";

            let text = roleText;
            if (game.game_over()) {
                if (game.in_checkmate()) text += " | 🏁 Мат! Игра окончена.";
                else text += " | 🤝 Ничья!";
            } else { 
                text += " | Ход: " + (game.turn() === 'w' ? 'Белых' : 'Черных'); 
            }
            document.getElementById('status').innerText = text;
        }
    </script>
</body>
</html>
"""