def get_home_page() -> str:
    return """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Шахматы с чатом</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Georgia', serif;
    background: #1a1a2e;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #e0e0e0;
  }
  .hero {
    text-align: center;
    margin-bottom: 40px;
  }
  .hero h1 {
    font-size: 3rem;
    color: #f0c040;
    text-shadow: 0 0 20px rgba(240,192,64,0.4);
    margin-bottom: 8px;
  }
  .hero p { color: #aaa; font-size: 1.1rem; }
  .card {
    background: #16213e;
    border: 1px solid #2a2a5a;
    border-radius: 12px;
    padding: 32px 40px;
    width: 360px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  }
  .input-group { margin-bottom: 16px; }
  .input-group label {
    display: block;
    font-size: 0.85rem;
    color: #aaa;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  input[type=text] {
    width: 100%;
    padding: 10px 14px;
    background: #0f3460;
    border: 1px solid #2a2a5a;
    border-radius: 8px;
    color: #fff;
    font-size: 1rem;
    outline: none;
    transition: border-color 0.2s;
  }
  input[type=text]:focus { border-color: #f0c040; }
  .btn {
    width: 100%;
    padding: 12px;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s;
    margin-top: 8px;
  }
  .btn-primary {
    background: #f0c040;
    color: #1a1a2e;
    font-weight: bold;
  }
  .btn-primary:hover { background: #ffd060; transform: translateY(-1px); }
  .btn-secondary {
    background: transparent;
    color: #f0c040;
    border: 1px solid #f0c040;
  }
  .btn-secondary:hover { background: rgba(240,192,64,0.1); }
  .divider {
    text-align: center;
    color: #555;
    margin: 16px 0;
    font-size: 0.85rem;
  }
  #error-msg {
    color: #ff6b6b;
    font-size: 0.85rem;
    margin-top: 10px;
    display: none;
  }
</style>
</head>
<body>
<div class="hero">
  <h1>♛ Шахматы</h1>
  <p>Играйте в реальном времени с чатом</p>
</div>
<div class="card">
  <div class="input-group">
    <label>Ваше имя</label>
    <input type="text" id="player-name" placeholder="Введите имя..." maxlength="30" value="">
  </div>
  <button class="btn btn-primary" onclick="createRoom()">🎲 Создать комнату</button>
  <div class="divider">— или —</div>
  <div class="input-group">
    <label>Код комнаты</label>
    <input type="text" id="room-id" placeholder="Введите код..." maxlength="8">
  </div>
  <button class="btn btn-secondary" onclick="joinRoom()">🚪 Войти в комнату</button>
  <div id="error-msg"></div>
</div>

<script>
  function getName() {
    return document.getElementById('player-name').value.trim() || 'Гость';
  }

  async function createRoom() {
    const name = getName();
    const resp = await fetch('/api/create-room', { method: 'POST' });
    const data = await resp.json();
    sessionStorage.setItem('playerName', name);
    window.location.href = '/room/' + data.room_id;
  }

  function joinRoom() {
    const name = getName();
    const rid = document.getElementById('room-id').value.trim();
    if (!rid) {
      showError('Введите код комнаты');
      return;
    }
    sessionStorage.setItem('playerName', name);
    window.location.href = '/room/' + rid;
  }

  function showError(msg) {
    const el = document.getElementById('error-msg');
    el.textContent = msg;
    el.style.display = 'block';
  }

  document.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      const rid = document.getElementById('room-id').value.trim();
      if (rid) joinRoom(); else createRoom();
    }
  });
</script>
</body>
</html>"""


def get_game_page(room_id: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Шахматы — комната {room_id}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Georgia', serif;
    background: #1a1a2e;
    color: #e0e0e0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }}

  /* ─── Шапка ─── */
  header {{
    background: #16213e;
    border-bottom: 1px solid #2a2a5a;
    padding: 10px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
  }}
  header h1 {{ font-size: 1.2rem; color: #f0c040; }}
  .room-code {{
    font-size: 0.8rem;
    background: #0f3460;
    border: 1px solid #2a2a5a;
    border-radius: 6px;
    padding: 4px 10px;
    color: #aaa;
    cursor: pointer;
    transition: background 0.2s;
  }}
  .room-code:hover {{ background: #1a4a80; color: #fff; }}
  #status-bar {{
    font-size: 0.85rem;
    padding: 4px 12px;
    border-radius: 20px;
    background: #0f3460;
    color: #aaa;
  }}

  /* ─── Основной layout ─── */
  main {{
    flex: 1;
    display: flex;
    gap: 16px;
    padding: 16px;
    overflow: hidden;
  }}

  /* ─── Шахматная доска ─── */
  .board-wrapper {{
    display: flex;
    flex-direction: column;
    align-items: center;
    flex-shrink: 0;
  }}
  .board-container {{
    position: relative;
    display: flex;
  }}
  .coords-file {{
    display: flex;
    padding-left: 24px;
    margin-bottom: 4px;
  }}
  .coords-file span, .coords-rank span {{
    font-size: 0.7rem;
    color: #666;
    text-align: center;
  }}
  .coords-file span {{ width: 62px; }}
  .coords-rank {{
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    padding-right: 4px;
    width: 20px;
  }}
  .coords-rank span {{ font-size: 0.7rem; color: #666; text-align: right; line-height: 62px; }}

  #board {{
    display: grid;
    grid-template-columns: repeat(8, 62px);
    grid-template-rows: repeat(8, 62px);
    border: 3px solid #f0c040;
    border-radius: 4px;
    overflow: hidden;
    box-shadow: 0 0 30px rgba(240,192,64,0.15);
  }}

  .sq {{
    width: 62px;
    height: 62px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.6rem;
    cursor: pointer;
    position: relative;
    user-select: none;
    transition: background 0.1s;
  }}
  .sq.light {{ background: #f0d9b5; }}
  .sq.dark  {{ background: #b58863; }}
  .sq.selected  {{ background: #7fc97f !important; }}
  .sq.legal     {{ cursor: pointer; }}
  .sq.legal::after {{
    content: '';
    position: absolute;
    width: 22px;
    height: 22px;
    background: rgba(0,0,0,0.18);
    border-radius: 50%;
    pointer-events: none;
  }}
  .sq.last-from {{ background: rgba(255,235,59,0.55) !important; }}
  .sq.last-to   {{ background: rgba(255,235,59,0.35) !important; }}
  .sq.check-king {{ background: rgba(220,30,30,0.6) !important; }}

  .piece-white {{ color: #fff; text-shadow: 0 0 3px #000, 0 0 6px rgba(0,0,0,0.8); }}
  .piece-black {{ color: #1a1a1a; text-shadow: 0 0 3px #fff, 0 0 4px rgba(255,255,255,0.5); }}

  .board-info {{
    margin-top: 10px;
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
    justify-content: center;
  }}
  .player-tag {{
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    border: 1px solid transparent;
  }}
  .player-tag.white {{ background: #e8e8e8; color: #1a1a2e; }}
  .player-tag.black {{ background: #2a2a2a; color: #e0e0e0; border-color: #555; }}
  .player-tag.active {{ border-color: #f0c040 !important; box-shadow: 0 0 8px rgba(240,192,64,0.4); }}

  #reset-btn {{
    padding: 5px 14px;
    background: transparent;
    border: 1px solid #555;
    border-radius: 20px;
    color: #aaa;
    cursor: pointer;
    font-size: 0.8rem;
    transition: all 0.2s;
  }}
  #reset-btn:hover {{ border-color: #f0c040; color: #f0c040; }}

  /* ─── Чат ─── */
  .chat-panel {{
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    background: #16213e;
    border: 1px solid #2a2a5a;
    border-radius: 12px;
    overflow: hidden;
    max-width: 380px;
  }}
  .chat-header {{
    padding: 12px 16px;
    border-bottom: 1px solid #2a2a5a;
    font-size: 0.85rem;
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  #chat-messages {{
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}
  #chat-messages::-webkit-scrollbar {{ width: 4px; }}
  #chat-messages::-webkit-scrollbar-thumb {{ background: #2a2a5a; border-radius: 2px; }}
  .msg {{
    font-size: 0.88rem;
    line-height: 1.4;
    padding: 6px 10px;
    border-radius: 8px;
    word-break: break-word;
  }}
  .msg.system {{
    background: rgba(240,192,64,0.08);
    color: #aaa;
    font-style: italic;
    text-align: center;
    font-size: 0.8rem;
  }}
  .msg.normal {{ background: rgba(255,255,255,0.04); }}
  .msg .sender {{
    font-weight: bold;
    margin-right: 6px;
    color: #f0c040;
  }}
  .msg.sender-black .sender {{ color: #c8c8c8; }}
  .msg.self .sender {{ color: #7fc97f; }}
  .msg .text {{ color: #ccc; }}
  .chat-input-row {{
    display: flex;
    padding: 10px 12px;
    border-top: 1px solid #2a2a5a;
    gap: 8px;
  }}
  #chat-input {{
    flex: 1;
    background: #0f3460;
    border: 1px solid #2a2a5a;
    border-radius: 8px;
    padding: 8px 12px;
    color: #fff;
    font-size: 0.9rem;
    font-family: inherit;
    outline: none;
    transition: border-color 0.2s;
  }}
  #chat-input:focus {{ border-color: #f0c040; }}
  #send-btn {{
    background: #f0c040;
    color: #1a1a2e;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    cursor: pointer;
    font-weight: bold;
    font-size: 0.9rem;
    transition: background 0.2s;
  }}
  #send-btn:hover {{ background: #ffd060; }}

  /* ─── Попап промоции ─── */
  #promo-modal {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.7);
    z-index: 100;
    align-items: center;
    justify-content: center;
  }}
  #promo-modal.visible {{ display: flex; }}
  .promo-box {{
    background: #16213e;
    border: 2px solid #f0c040;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
  }}
  .promo-box h3 {{ margin-bottom: 14px; color: #f0c040; }}
  .promo-btns {{ display: flex; gap: 10px; }}
  .promo-btn {{
    width: 60px;
    height: 60px;
    font-size: 2.2rem;
    background: #0f3460;
    border: 1px solid #2a2a5a;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s;
  }}
  .promo-btn:hover {{ background: #1a4a80; }}

  /* ─── Оверлей конца игры ─── */
  #game-over-overlay {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.75);
    z-index: 200;
    align-items: center;
    justify-content: center;
  }}
  #game-over-overlay.visible {{ display: flex; }}
  .game-over-box {{
    background: #16213e;
    border: 2px solid #f0c040;
    border-radius: 16px;
    padding: 36px 48px;
    text-align: center;
  }}
  .game-over-box h2 {{ font-size: 2rem; color: #f0c040; margin-bottom: 10px; }}
  .game-over-box p {{ color: #aaa; margin-bottom: 20px; }}
  .game-over-box button {{
    padding: 10px 24px;
    background: #f0c040;
    color: #1a1a2e;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: bold;
    cursor: pointer;
  }}

  /* ─── Индикатор соединения ─── */
  #conn-indicator {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #ff6b6b;
    display: inline-block;
    margin-right: 6px;
    transition: background 0.3s;
  }}
  #conn-indicator.connected {{ background: #6bcb77; }}

  @media (max-width: 900px) {{
    main {{ flex-direction: column; overflow: auto; }}
    .chat-panel {{ max-width: 100%; min-height: 300px; }}
    .sq {{ width: 44px; height: 44px; font-size: 1.9rem; }}
    #board {{ grid-template-columns: repeat(8, 44px); grid-template-rows: repeat(8, 44px); }}
    .coords-file span {{ width: 44px; }}
    .coords-rank span {{ line-height: 44px; }}
  }}
</style>
</head>
<body>

<header>
  <h1>♛ Шахматы</h1>
  <span id="status-bar"><span id="conn-indicator"></span>Подключение...</span>
  <span class="room-code" onclick="copyRoomCode()" title="Скопировать код комнаты">
    Комната: <strong>{room_id}</strong>
  </span>
</header>

<main>
  <div class="board-wrapper">
    <div class="coords-file" id="file-labels"></div>
    <div class="board-container">
      <div class="coords-rank" id="rank-labels"></div>
      <div id="board"></div>
    </div>
    <div class="board-info">
      <span class="player-tag white" id="tag-white">⬜ Ожидание...</span>
      <span class="player-tag black" id="tag-black">⬛ Ожидание...</span>
      <button id="reset-btn" onclick="sendReset()">↺ Новая игра</button>
    </div>
  </div>

  <div class="chat-panel">
    <div class="chat-header">💬 Чат</div>
    <div id="chat-messages"></div>
    <div class="chat-input-row">
      <input type="text" id="chat-input" placeholder="Написать в чат..." maxlength="500">
      <button id="send-btn" onclick="sendChat()">➤</button>
    </div>
  </div>
</main>

<!-- Попап выбора промоции -->
<div id="promo-modal">
  <div class="promo-box">
    <h3>Выберите фигуру</h3>
    <div class="promo-btns">
      <button class="promo-btn" onclick="confirmPromotion('q')">♛</button>
      <button class="promo-btn" onclick="confirmPromotion('r')">♜</button>
      <button class="promo-btn" onclick="confirmPromotion('b')">♝</button>
      <button class="promo-btn" onclick="confirmPromotion('n')">♞</button>
    </div>
  </div>
</div>

<!-- Конец игры -->
<div id="game-over-overlay">
  <div class="game-over-box">
    <h2 id="game-over-title">Игра окончена</h2>
    <p id="game-over-sub"></p>
    <button onclick="sendReset(); hideGameOver()">↺ Новая игра</button>
  </div>
</div>

<script>
// ─── Константы ───────────────────────────────────────────────────────────────
const ROOM_ID = "{room_id}";
const FILES = ['a','b','c','d','e','f','g','h'];
const RANKS = ['8','7','6','5','4','3','2','1'];

// Unicode-фигуры: заглавная = белая, строчная = чёрная
const PIECE_UNICODE = {{
  'K':'♔','Q':'♕','R':'♖','B':'♗','N':'♘','P':'♙',
  'k':'♚','q':'♛','r':'♜','b':'♝','n':'♞','p':'♟'
}};

// ─── Состояние ───────────────────────────────────────────────────────────────
let ws = null;
let myColor = null;
let myName = sessionStorage.getItem('playerName') || 'Гость';
let currentTurn = 'white';
let selectedSq = null;     // выбранная клетка (строка "e2")
let pendingMove = null;    // ожидающий промоции: {{from, to}}
let lastMove = null;       // {{from, to}} последний ход
let currentBoard = null;   // текущий двумерный массив
let isFlipped = false;     // перевёрнута ли доска

// ─── WebSocket с переподключением ────────────────────────────────────────────
let reconnectAttempts = 0;
let reconnectTimer = null;

function connect() {{
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${{proto}}://${{location.host}}/ws/${{ROOM_ID}}`);

  ws.onopen = () => {{
    reconnectAttempts = 0;
    setConnStatus(true);
    ws.send(JSON.stringify({{ type: 'join', name: myName }}));
  }};

  ws.onmessage = (evt) => {{
    try {{ handleMessage(JSON.parse(evt.data)); }}
    catch(e) {{ console.error('parse error', e); }}
  }};

  ws.onclose = () => {{
    setConnStatus(false);
    scheduleReconnect();
  }};

  ws.onerror = () => {{ ws.close(); }};
}}

function scheduleReconnect() {{
  if (reconnectTimer) return;
  const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 16000);
  reconnectAttempts++;
  document.getElementById('status-bar').innerHTML =
    '<span id="conn-indicator"></span>Переподключение...';
  reconnectTimer = setTimeout(() => {{
    reconnectTimer = null;
    connect();
  }}, delay);
}}

function setConnStatus(online) {{
  const ind = document.getElementById('conn-indicator');
  if (ind) ind.className = online ? 'connected' : '';
}}

// ─── Обработка сообщений от сервера ─────────────────────────────────────────
function handleMessage(data) {{
  if (data.type === 'init') {{
    myColor = data.color;
    currentTurn = data.turn;
    isFlipped = (myColor === 'black');
    buildCoords();
    renderBoard(data.board);
    updateTurnIndicator(data.turn);
    updateStatusBar(data.color);
    // Восстановить историю чата
    if (data.chat && data.chat.length) {{
      data.chat.forEach(m => appendChat(m));
    }}
  }}
  else if (data.type === 'update') {{
    currentTurn = data.turn;
    lastMove = data.last_move;
    renderBoard(data.board);
    updateTurnIndicator(data.turn);
    handleGameStatus(data.status, data.winner);
  }}
  else if (data.type === 'chat') {{
    appendChat(data);
  }}
  else if (data.type === 'error') {{
    showError(data.text);
    selectedSq = null;
    renderBoard(currentBoard);
  }}
}}

// ─── Рендер доски ────────────────────────────────────────────────────────────
function sqName(row, col) {{
  // row=0 => rank 8, col=0 => file a  (при нормальной ориентации)
  if (!isFlipped) {{
    return FILES[col] + (8 - row);
  }} else {{
    return FILES[7 - col] + (row + 1);
  }}
}}

function rowColFromSq(sq) {{
  const file = FILES.indexOf(sq[0]);
  const rank = parseInt(sq[1]);
  if (!isFlipped) {{
    return {{ row: 8 - rank, col: file }};
  }} else {{
    return {{ row: rank - 1, col: 7 - file }};
  }}
}}

function renderBoard(board) {{
  currentBoard = board;
  const el = document.getElementById('board');
  el.innerHTML = '';

  // Собираем легальные ходы для выделения
  const legalTargets = new Set();
  // (легальные ходы считаются на сервере, здесь только подсветка выбранной)

  for (let row = 0; row < 8; row++) {{
    for (let col = 0; col < 8; col++) {{
      const sq = sqName(row, col);
      const isLight = (row + col) % 2 === 0;

      // Берём фигуру из массива: board[row][col] при нормальной ориентации
      let piece;
      if (!isFlipped) {{
        piece = board[row][col];
      }} else {{
        piece = board[7 - row][7 - col];
      }}

      const div = document.createElement('div');
      div.className = 'sq ' + (isLight ? 'light' : 'dark');
      div.dataset.sq = sq;

      // Подсветка последнего хода
      if (lastMove) {{
        if (sq === lastMove.from) div.classList.add('last-from');
        if (sq === lastMove.to)   div.classList.add('last-to');
      }}

      // Подсветка выбранной клетки
      if (selectedSq === sq) div.classList.add('selected');

      // Фигура
      if (piece) {{
        const isWhitePiece = piece === piece.toUpperCase();
        const span = document.createElement('span');
        span.textContent = PIECE_UNICODE[piece] || piece;
        span.className = isWhitePiece ? 'piece-white' : 'piece-black';
        div.appendChild(span);
      }}

      div.onclick = () => handleSquareClick(sq, div);
      el.appendChild(div);
    }}
  }}
}}

// ─── Логика кликов ───────────────────────────────────────────────────────────
function handleSquareClick(sq, div) {{
  if (!myColor || myColor !== currentTurn) return;

  const piece = getPieceAt(sq);
  const isMyPiece = piece && (
    (myColor === 'white' && piece === piece.toUpperCase()) ||
    (myColor === 'black' && piece === piece.toLowerCase())
  );

  if (!selectedSq) {{
    if (isMyPiece) {{
      selectedSq = sq;
      renderBoard(currentBoard);
    }}
  }} else {{
    if (selectedSq === sq) {{
      selectedSq = null;
      renderBoard(currentBoard);
      return;
    }}
    if (isMyPiece) {{
      selectedSq = sq;
      renderBoard(currentBoard);
      return;
    }}
    // Пробуем сделать ход
    const fromPiece = getPieceAt(selectedSq);
    const isPawn = fromPiece && fromPiece.toLowerCase() === 'p';
    const toRank = sq[1];
    const isPromo = isPawn && ((myColor === 'white' && toRank === '8') ||
                               (myColor === 'black' && toRank === '1'));

    if (isPromo) {{
      pendingMove = {{ from: selectedSq, to: sq }};
      selectedSq = null;
      document.getElementById('promo-modal').classList.add('visible');
    }} else {{
      const from = selectedSq;
      selectedSq = null;
      sendMove(from, sq, null);
    }}
  }}
}}

function getPieceAt(sq) {{
  if (!currentBoard) return null;
  const file = FILES.indexOf(sq[0]);
  const rank = parseInt(sq[1]);
  return currentBoard[8 - rank][file];
}}

// ─── Промоция ────────────────────────────────────────────────────────────────
function confirmPromotion(piece) {{
  document.getElementById('promo-modal').classList.remove('visible');
  if (pendingMove) {{
    sendMove(pendingMove.from, pendingMove.to, piece);
    pendingMove = null;
  }}
}}

// ─── Отправка ходов ──────────────────────────────────────────────────────────
function sendMove(from, to, promotion) {{
  if (!ws || ws.readyState !== 1) return;
  ws.send(JSON.stringify({{ type:'move', from, to, promotion: promotion||'q' }}));
}}

function sendChat() {{
  const inp = document.getElementById('chat-input');
  const text = inp.value.trim();
  if (!text || !ws || ws.readyState !== 1) return;
  ws.send(JSON.stringify({{ type:'chat', text }}));
  inp.value = '';
}}

function sendReset() {{
  if (!ws || ws.readyState !== 1) return;
  lastMove = null;
  selectedSq = null;
  ws.send(JSON.stringify({{ type:'reset' }}));
}}

// ─── Чат ─────────────────────────────────────────────────────────────────────
function appendChat(msg) {{
  const box = document.getElementById('chat-messages');
  const div = document.createElement('div');

  if (msg.system) {{
    div.className = 'msg system';
    div.textContent = msg.text;
  }} else {{
    const isSelf = msg.sender === myName;
    div.className = 'msg normal' +
      (isSelf ? ' self' : '') +
      (msg.color === 'black' ? ' sender-black' : '');
    div.innerHTML = `<span class="sender">${{msg.sender}}:</span><span class="text">${{escHtml(msg.text)}}</span>`;
  }}

  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}}

function escHtml(s) {{
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}

// ─── UI helpers ──────────────────────────────────────────────────────────────
function buildCoords() {{
  const fileEl = document.getElementById('file-labels');
  const rankEl = document.getElementById('rank-labels');
  fileEl.innerHTML = '';
  rankEl.innerHTML = '';

  const files = isFlipped ? [...FILES].reverse() : FILES;
  const ranks = isFlipped ? [...RANKS].reverse() : RANKS;

  files.forEach(f => {{
    const span = document.createElement('span');
    span.textContent = f;
    fileEl.appendChild(span);
  }});
  ranks.forEach(r => {{
    const span = document.createElement('span');
    span.textContent = r;
    rankEl.appendChild(span);
  }});
}}

function updateTurnIndicator(turn) {{
  document.getElementById('tag-white').classList.toggle('active', turn === 'white');
  document.getElementById('tag-black').classList.toggle('active', turn === 'black');
}}

function updateStatusBar(color) {{
  const label = {{ white:'⬜ Вы играете белыми', black:'⬛ Вы играете чёрными' }}[color] || '👁 Вы зритель';
  document.getElementById('status-bar').innerHTML =
    `<span id="conn-indicator" class="connected"></span>${{label}}`;
}}

function showError(text) {{
  appendChat({{ system: true, text: '⚠ ' + text }});
}}

function handleGameStatus(status, winner) {{
  if (status === 'checkmate') {{
    const winName = winner === 'white' ? '⬜ Белые' : '⬛ Чёрные';
    showGameOver('Мат!', winName + ' победили 🏆');
  }} else if (status === 'stalemate') {{
    showGameOver('Пат!', 'Ничья — нет допустимых ходов');
  }} else if (status === 'check') {{
    appendChat({{ system: true, text: '⚡ Шах!' }});
  }}
}}

function showGameOver(title, sub) {{
  document.getElementById('game-over-title').textContent = title;
  document.getElementById('game-over-sub').textContent = sub;
  document.getElementById('game-over-overlay').classList.add('visible');
}}

function hideGameOver() {{
  document.getElementById('game-over-overlay').classList.remove('visible');
}}

function copyRoomCode() {{
  navigator.clipboard.writeText('{room_id}').then(() => {{
    appendChat({{ system: true, text: 'Код комнаты скопирован: {room_id}' }});
  }});
}}

// ─── Горячие клавиши ─────────────────────────────────────────────────────────
document.getElementById('chat-input').addEventListener('keydown', e => {{
  if (e.key === 'Enter') sendChat();
}});

// Старт
connect();
</script>
</body>
</html>"""