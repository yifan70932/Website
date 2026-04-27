/* ============================================================
   yifanova.com — interactive chess board (chess.js)
   ------------------------------------------------------------
   A single chess board widget that:
   - Displays the standard 8×8 starting position.
   - Lets two humans play out a full game.
   - Supports check, checkmate, stalemate.
   - Streams a Stockfish (WASM) analysis of the current position
     in the panel below the board: evaluation + best move.
   - Bilingual UI (English / Chinese) via lang attribute.
   ============================================================ */

(function() {
"use strict";

document.addEventListener('DOMContentLoaded', function() {
  const root = document.querySelector('.chess-widget');
  if (!root) return;
  
  const lang = (document.documentElement.lang || 'en').slice(0, 2);
  const t = lang === 'zh' ? STRINGS.zh : STRINGS.en;

  // ─── Game state ────────────────────────────────────────
  // Board: 8×8 array. Index [row][col]. Row 0 is rank 8 (Black back), row 7 is rank 1 (White back).
  // Each cell: { type: 'p'|'n'|'b'|'r'|'q'|'k', color: 'w'|'b' } or null.
  
  function initialBoard() {
    const back = ['r','n','b','q','k','b','n','r'];
    const board = [];
    for (let r = 0; r < 8; r++) {
      board.push([null, null, null, null, null, null, null, null]);
    }
    // Black back rank
    for (let c = 0; c < 8; c++) board[0][c] = { type: back[c], color: 'b' };
    for (let c = 0; c < 8; c++) board[1][c] = { type: 'p', color: 'b' };
    for (let c = 0; c < 8; c++) board[6][c] = { type: 'p', color: 'w' };
    for (let c = 0; c < 8; c++) board[7][c] = { type: back[c], color: 'w' };
    return board;
  }
  
  let state = {
    board: initialBoard(),
    turn: 'w',          // 'w' or 'b'
    selected: null,     // {row, col} of currently-clicked piece, or null
    legalMoves: [],     // array of {row, col, special?} for the selected piece
    castlingRights: { wK: true, wQ: true, bK: true, bQ: true },
    enPassantTarget: null,  // {row, col} or null
    moveHistory: [],    // array of move records for undo
    gameOver: null,     // null | 'checkmate-w' | 'checkmate-b' | 'stalemate' | 'draw'
  };

  // ─── Piece movement: pseudo-legal moves (not yet checking for own king in check) ──
  
  function isInside(r, c) {
    return r >= 0 && r < 8 && c >= 0 && c < 8;
  }
  
  function pieceAt(board, r, c) {
    if (!isInside(r, c)) return null;
    return board[r][c];
  }
  
  function pseudoMoves(board, r, c, castlingRights, enPassantTarget) {
    const piece = board[r][c];
    if (!piece) return [];
    const moves = [];
    const dir = piece.color === 'w' ? -1 : 1;  // white moves up (toward row 0)
    
    if (piece.type === 'p') {
      // Pawn: forward 1, forward 2 from start, diagonal capture, en passant.
      const startRow = piece.color === 'w' ? 6 : 1;
      // Forward one
      if (isInside(r + dir, c) && !pieceAt(board, r + dir, c)) {
        moves.push({ row: r + dir, col: c });
        // Forward two from start
        if (r === startRow && !pieceAt(board, r + 2 * dir, c)) {
          moves.push({ row: r + 2 * dir, col: c, special: 'pawn-double' });
        }
      }
      // Diagonal captures
      for (const dc of [-1, 1]) {
        const target = pieceAt(board, r + dir, c + dc);
        if (target && target.color !== piece.color) {
          moves.push({ row: r + dir, col: c + dc });
        }
        // En passant
        if (enPassantTarget && enPassantTarget.row === r + dir && enPassantTarget.col === c + dc) {
          moves.push({ row: r + dir, col: c + dc, special: 'en-passant' });
        }
      }
    }
    else if (piece.type === 'n') {
      const offsets = [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]];
      for (const [dr, dc] of offsets) {
        const nr = r + dr, nc = c + dc;
        if (!isInside(nr, nc)) continue;
        const target = board[nr][nc];
        if (!target || target.color !== piece.color) {
          moves.push({ row: nr, col: nc });
        }
      }
    }
    else if (piece.type === 'b' || piece.type === 'r' || piece.type === 'q') {
      const dirs = [];
      if (piece.type !== 'b') dirs.push([-1,0],[1,0],[0,-1],[0,1]);  // rook directions
      if (piece.type !== 'r') dirs.push([-1,-1],[-1,1],[1,-1],[1,1]); // bishop directions
      for (const [dr, dc] of dirs) {
        let nr = r + dr, nc = c + dc;
        while (isInside(nr, nc)) {
          const target = board[nr][nc];
          if (!target) {
            moves.push({ row: nr, col: nc });
          } else {
            if (target.color !== piece.color) moves.push({ row: nr, col: nc });
            break;
          }
          nr += dr; nc += dc;
        }
      }
    }
    else if (piece.type === 'k') {
      for (let dr = -1; dr <= 1; dr++) {
        for (let dc = -1; dc <= 1; dc++) {
          if (dr === 0 && dc === 0) continue;
          const nr = r + dr, nc = c + dc;
          if (!isInside(nr, nc)) continue;
          const target = board[nr][nc];
          if (!target || target.color !== piece.color) {
            moves.push({ row: nr, col: nc });
          }
        }
      }
      // Castling
      const homeRow = piece.color === 'w' ? 7 : 0;
      const cr = castlingRights;
      const canK = piece.color === 'w' ? cr.wK : cr.bK;
      const canQ = piece.color === 'w' ? cr.wQ : cr.bQ;
      if (r === homeRow && c === 4) {
        if (canK && !board[homeRow][5] && !board[homeRow][6] &&
            board[homeRow][7] && board[homeRow][7].type === 'r' && board[homeRow][7].color === piece.color) {
          moves.push({ row: homeRow, col: 6, special: 'castle-K' });
        }
        if (canQ && !board[homeRow][1] && !board[homeRow][2] && !board[homeRow][3] &&
            board[homeRow][0] && board[homeRow][0].type === 'r' && board[homeRow][0].color === piece.color) {
          moves.push({ row: homeRow, col: 2, special: 'castle-Q' });
        }
      }
    }
    return moves;
  }
  
  function findKing(board, color) {
    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 8; c++) {
        const p = board[r][c];
        if (p && p.type === 'k' && p.color === color) return { row: r, col: c };
      }
    }
    return null;
  }
  
  function isSquareAttacked(board, row, col, byColor) {
    // Is the square (row, col) attacked by any piece of byColor?
    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 8; c++) {
        const p = board[r][c];
        if (!p || p.color !== byColor) continue;
        // For attack purposes, pawns attack only diagonally.
        if (p.type === 'p') {
          const dir = p.color === 'w' ? -1 : 1;
          if (r + dir === row && (c - 1 === col || c + 1 === col)) return true;
        } else {
          // Use pseudoMoves but disable castling check (irrelevant for attack)
          const cr = { wK: false, wQ: false, bK: false, bQ: false };
          const ms = pseudoMoves(board, r, c, cr, null);
          for (const m of ms) {
            if (m.row === row && m.col === col) return true;
          }
        }
      }
    }
    return false;
  }
  
  function isInCheck(board, color) {
    const k = findKing(board, color);
    if (!k) return false;
    return isSquareAttacked(board, k.row, k.col, color === 'w' ? 'b' : 'w');
  }
  
  function applyMove(board, fromR, fromC, toR, toC, special, castlingRights) {
    // Returns { newBoard, newCastlingRights, newEnPassantTarget, captured }.
    const newBoard = board.map(row => row.slice());
    const piece = newBoard[fromR][fromC];
    let captured = newBoard[toR][toC];
    
    newBoard[toR][toC] = piece;
    newBoard[fromR][fromC] = null;
    
    let newEnPassant = null;
    
    if (special === 'pawn-double') {
      newEnPassant = { row: (fromR + toR) / 2, col: toC };
    }
    else if (special === 'en-passant') {
      // Captured pawn is on (fromR, toC)
      captured = newBoard[fromR][toC];
      newBoard[fromR][toC] = null;
    }
    else if (special === 'castle-K') {
      newBoard[toR][5] = newBoard[toR][7];
      newBoard[toR][7] = null;
    }
    else if (special === 'castle-Q') {
      newBoard[toR][3] = newBoard[toR][0];
      newBoard[toR][0] = null;
    }
    
    // Pawn promotion to queen (auto-promote for simplicity)
    if (piece.type === 'p' && (toR === 0 || toR === 7)) {
      newBoard[toR][toC] = { type: 'q', color: piece.color };
    }
    
    // Update castling rights
    const newCR = { ...castlingRights };
    if (piece.type === 'k') {
      if (piece.color === 'w') { newCR.wK = false; newCR.wQ = false; }
      else { newCR.bK = false; newCR.bQ = false; }
    }
    if (piece.type === 'r') {
      if (fromR === 7 && fromC === 0) newCR.wQ = false;
      if (fromR === 7 && fromC === 7) newCR.wK = false;
      if (fromR === 0 && fromC === 0) newCR.bQ = false;
      if (fromR === 0 && fromC === 7) newCR.bK = false;
    }
    // If a rook is captured on its home square, lose those rights too
    if (toR === 7 && toC === 0) newCR.wQ = false;
    if (toR === 7 && toC === 7) newCR.wK = false;
    if (toR === 0 && toC === 0) newCR.bQ = false;
    if (toR === 0 && toC === 7) newCR.bK = false;
    
    return { newBoard, newCastlingRights: newCR, newEnPassantTarget: newEnPassant, captured };
  }
  
  function legalMoves(board, r, c, castlingRights, enPassantTarget) {
    // Filter pseudo-moves: a move is legal if it doesn't leave own king in check.
    // Castling has additional rules: can't castle through check or while in check.
    const piece = board[r][c];
    if (!piece) return [];
    const candidates = pseudoMoves(board, r, c, castlingRights, enPassantTarget);
    const out = [];
    for (const m of candidates) {
      // Castling-specific filtering
      if (m.special === 'castle-K' || m.special === 'castle-Q') {
        if (isInCheck(board, piece.color)) continue;
        const homeRow = r;
        const cols = m.special === 'castle-K' ? [4, 5, 6] : [4, 3, 2];
        let ok = true;
        for (const cc of cols) {
          if (isSquareAttacked(board, homeRow, cc, piece.color === 'w' ? 'b' : 'w')) {
            ok = false; break;
          }
        }
        if (!ok) continue;
      }
      const { newBoard } = applyMove(board, r, c, m.row, m.col, m.special, castlingRights);
      if (!isInCheck(newBoard, piece.color)) {
        out.push(m);
      }
    }
    return out;
  }
  
  function hasAnyLegalMove(board, color, castlingRights, enPassantTarget) {
    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 8; c++) {
        const p = board[r][c];
        if (!p || p.color !== color) continue;
        if (legalMoves(board, r, c, castlingRights, enPassantTarget).length > 0) return true;
      }
    }
    return false;
  }
  
  // ─── FEN conversion ───────────────────────────────────
  // Build a FEN string describing the current state, for Stockfish.
  
  function toFEN(state) {
    const FEN_MAP = { p:'p', n:'n', b:'b', r:'r', q:'q', k:'k' };
    let fenRows = [];
    for (let r = 0; r < 8; r++) {
      let row = '';
      let empty = 0;
      for (let c = 0; c < 8; c++) {
        const p = state.board[r][c];
        if (!p) {
          empty++;
        } else {
          if (empty > 0) { row += empty; empty = 0; }
          let ch = FEN_MAP[p.type];
          row += p.color === 'w' ? ch.toUpperCase() : ch;
        }
      }
      if (empty > 0) row += empty;
      fenRows.push(row);
    }
    const board = fenRows.join('/');
    const turn = state.turn;
    const cr = state.castlingRights;
    let castle = '';
    if (cr.wK) castle += 'K';
    if (cr.wQ) castle += 'Q';
    if (cr.bK) castle += 'k';
    if (cr.bQ) castle += 'q';
    if (!castle) castle = '-';
    let ep = '-';
    if (state.enPassantTarget) {
      const file = String.fromCharCode(97 + state.enPassantTarget.col);
      const rank = 8 - state.enPassantTarget.row;
      ep = file + rank;
    }
    // Halfmove clock and fullmove number — we don't track these, set defaults.
    return `${board} ${turn} ${castle} ${ep} 0 1`;
  }

  // ─── Stockfish (WASM) integration ──────────────────────
  
  // Stockfish files are self-hosted at /assets/sf/. We detect WebAssembly
  // support and pick the WASM build (smaller + faster) or fall back to
  // the asm.js single-file build for browsers without WASM.
  const SF_BASE = '/assets/sf/';
  const WASM_SUPPORTED = (typeof WebAssembly === 'object'
    && typeof WebAssembly.validate === 'function'
    && WebAssembly.validate(Uint8Array.of(0x00,0x61,0x73,0x6d,0x01,0x00,0x00,0x00)));
  const SF_URL = SF_BASE + (WASM_SUPPORTED ? 'stockfish.wasm.js' : 'stockfish.js');
  
  let sfWorker = null;
  let sfReady = false;
  let sfFailed = false;
  let sfPendingFen = null;  // queued analysis request
  let sfAnalyzing = false;
  let sfLastInfo = null;    // {evalCp, mateIn, depth, bestMove, bestSan}
  
  function initStockfish() {
    try {
      sfWorker = new Worker(SF_URL);
      sfWorker.addEventListener('message', onSfMessage);
      sfWorker.addEventListener('error', () => {
        sfFailed = true;
        renderSf();
      });
      sfWorker.postMessage('uci');
    } catch (e) {
      sfFailed = true;
      renderSf();
    }
  }
  
  function onSfMessage(e) {
    const line = (typeof e.data === 'string') ? e.data : '';
    if (!line) return;
    
    if (line === 'uciok') {
      sfWorker.postMessage('setoption name Hash value 16');
      sfWorker.postMessage('isready');
      return;
    }
    if (line === 'readyok') {
      sfReady = true;
      renderSf();
      // Kick off any queued analysis
      if (sfPendingFen) {
        const fen = sfPendingFen;
        sfPendingFen = null;
        analyze(fen);
      } else {
        // Default: analyze current position
        analyze(toFEN(state));
      }
      return;
    }
    
    // Parse "info ... depth N ... score cp X" or "score mate Y" lines, also "pv ..."
    if (line.startsWith('info ')) {
      const m = line.match(/\bdepth\s+(\d+)/);
      const cp = line.match(/\bscore\s+cp\s+(-?\d+)/);
      const mate = line.match(/\bscore\s+mate\s+(-?\d+)/);
      const pv = line.match(/\bpv\s+(\S+)/);
      if (m) {
        const info = { depth: parseInt(m[1], 10) };
        if (cp) info.evalCp = parseInt(cp[1], 10);
        if (mate) info.mateIn = parseInt(mate[1], 10);
        if (pv) info.bestMove = pv[1];
        sfLastInfo = Object.assign({}, sfLastInfo, info);
        renderSf();
      }
      return;
    }
    if (line.startsWith('bestmove')) {
      const parts = line.split(/\s+/);
      if (parts[1]) {
        sfLastInfo = sfLastInfo || {};
        sfLastInfo.bestMove = parts[1];
      }
      sfAnalyzing = false;
      renderSf();
      // If a new request came in while analyzing, run it now
      if (sfPendingFen) {
        const fen = sfPendingFen;
        sfPendingFen = null;
        analyze(fen);
      }
      return;
    }
  }
  
  function analyze(fen) {
    if (!sfWorker || !sfReady || sfFailed) return;
    if (sfAnalyzing) {
      sfPendingFen = fen;
      sfWorker.postMessage('stop');
      return;
    }
    sfLastInfo = { depth: 0 };
    sfAnalyzing = true;
    sfWorker.postMessage('position fen ' + fen);
    sfWorker.postMessage('go depth 15');
    renderSf();
  }
  
  function uciToSan(uci) {
    // Just return the UCI move (e.g., "e2e4"); rendering it as SAN would
    // require re-running the engine on the position, which is more work
    // than necessary. UCI is readable enough for users.
    if (!uci || uci === '(none)') return '';
    // Pretty up the move slightly: e2e4 -> e2-e4
    if (uci.length === 4) return uci.slice(0, 2) + '–' + uci.slice(2, 4);
    if (uci.length === 5) return uci.slice(0, 2) + '–' + uci.slice(2, 4) + '=' + uci.slice(4).toUpperCase();
    return uci;
  }
  
  function formatEval(info, turn) {
    if (!info) return '—';
    if (info.mateIn != null) {
      // mate score is from side-to-move's perspective; convert to white-positive
      const m = info.mateIn;
      const sign = turn === 'w' ? (m > 0 ? '+' : '-') : (m > 0 ? '-' : '+');
      return sign + 'M' + Math.abs(m);
    }
    if (info.evalCp != null) {
      // engine returns from side-to-move's perspective; convert to always-white-positive
      const fromWhite = turn === 'w' ? info.evalCp : -info.evalCp;
      const v = fromWhite / 100;
      return (v >= 0 ? '+' : '') + v.toFixed(2);
    }
    return '—';
  }
  
  function evalToBarPercent(info, turn) {
    // Returns 0..100 representing white's share of the bar (from white-perspective).
    if (!info) return 50;
    if (info.mateIn != null) {
      const m = info.mateIn;
      const fromWhite = turn === 'w' ? m : -m;
      return fromWhite > 0 ? 100 : 0;
    }
    if (info.evalCp != null) {
      const fromWhite = turn === 'w' ? info.evalCp : -info.evalCp;
      // Map [-1000, +1000] cp to [0, 100] with sigmoid-ish smoothing.
      const cp = Math.max(-1000, Math.min(1000, fromWhite));
      // Linear-ish but compressed near extremes
      const t = cp / 1000;  // -1..1
      const pct = 50 + 50 * Math.sign(t) * Math.min(1, Math.abs(t) * 1.4);
      return Math.max(0, Math.min(100, pct));
    }
    return 50;
  }
  
  function renderSf() {
    const evalEl = root.querySelector('[data-role="sf-eval"]');
    const detailEl = root.querySelector('[data-role="sf-detail"]');
    const barEl = root.querySelector('[data-role="sf-bar-fill"]');
    if (!evalEl || !detailEl || !barEl) return;
    
    if (sfFailed) {
      evalEl.textContent = '—';
      detailEl.textContent = t.sfFailed;
      barEl.style.width = '50%';
      return;
    }
    if (!sfReady) {
      evalEl.textContent = '—';
      detailEl.textContent = t.sfLoading;
      barEl.style.width = '50%';
      return;
    }
    if (state.gameOver) {
      // Don't analyze finished games — show terminal eval
      let pct = 50;
      let lbl = '—';
      if (state.gameOver === 'checkmate-w') { pct = 0; lbl = '0–1'; }
      else if (state.gameOver === 'checkmate-b') { pct = 100; lbl = '1–0'; }
      else { pct = 50; lbl = '½–½'; }
      evalEl.textContent = lbl;
      detailEl.textContent = '';
      barEl.style.width = pct + '%';
      return;
    }
    
    const info = sfLastInfo;
    evalEl.textContent = formatEval(info, state.turn);
    barEl.style.width = evalToBarPercent(info, state.turn) + '%';
    
    let detail = '';
    if (info && info.depth) {
      detail = `${t.sfDepth} ${info.depth}`;
      if (info.bestMove) {
        detail += ` · ${t.sfBestMove} ${uciToSan(info.bestMove)}`;
      }
    } else if (sfAnalyzing) {
      detail = t.sfThinking;
    } else {
      detail = t.sfReady;
    }
    detailEl.textContent = detail;
  }


  
  // ─── Rendering ─────────────────────────────────────────
  
  const PIECE_GLYPHS = {
    'wk': '♔', 'wq': '♕', 'wr': '♖', 'wb': '♗', 'wn': '♘', 'wp': '♙',
    'bk': '♚', 'bq': '♛', 'br': '♜', 'bb': '♝', 'bn': '♞', 'bp': '♟',
  };
  
  function buildBoardDOM() {
    root.innerHTML = '';
    
    // Container with two parts: board on left, info panel on right
    const wrap = document.createElement('div');
    wrap.className = 'chess-wrap';
    
    const boardDiv = document.createElement('div');
    boardDiv.className = 'chess-board';
    
    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 8; c++) {
        const sq = document.createElement('button');
        sq.type = 'button';
        sq.className = 'chess-sq ' + ((r + c) % 2 === 0 ? 'light' : 'dark');
        sq.dataset.row = r;
        sq.dataset.col = c;
        // Coordinate labels: rank on leftmost column, file on bottom row.
        if (c === 0) {
          const rank = document.createElement('span');
          rank.className = 'chess-coord chess-coord-rank';
          rank.textContent = String(8 - r);
          sq.appendChild(rank);
        }
        if (r === 7) {
          const file = document.createElement('span');
          file.className = 'chess-coord chess-coord-file';
          file.textContent = String.fromCharCode(97 + c);
          sq.appendChild(file);
        }
        sq.setAttribute('aria-label', squareLabel(r, c));
        sq.addEventListener('click', () => handleSquareClick(r, c));
        boardDiv.appendChild(sq);
      }
    }
    
    const info = document.createElement('div');
    info.className = 'chess-info';
    info.innerHTML = `
      <div class="chess-status" data-role="status"></div>
      <div class="chess-controls">
        <button type="button" data-role="undo">${t.undo}</button>
        <button type="button" data-role="reset">${t.reset}</button>
      </div>
    `;
    
    // Stockfish analysis panel — separate row below status/controls
    const sf = document.createElement('div');
    sf.className = 'chess-sf';
    sf.innerHTML = `
      <div class="chess-sf-bar"><div class="chess-sf-bar-fill" data-role="sf-bar-fill"></div></div>
      <div class="chess-sf-readout">
        <span class="chess-sf-eval" data-role="sf-eval">—</span>
        <span class="chess-sf-detail" data-role="sf-detail">${t.sfLoading}</span>
      </div>
    `;
    
    wrap.appendChild(boardDiv);
    wrap.appendChild(info);
    wrap.appendChild(sf);
    root.appendChild(wrap);
    
    info.querySelector('[data-role="reset"]').addEventListener('click', resetGame);
    info.querySelector('[data-role="undo"]').addEventListener('click', undoMove);
  }
  
  function squareLabel(r, c) {
    const file = String.fromCharCode(97 + c);  // a..h
    const rank = 8 - r;
    return file + rank;
  }
  
  function render() {
    // Update each square: piece glyph, highlights
    const squares = root.querySelectorAll('.chess-sq');
    squares.forEach(sq => {
      const r = parseInt(sq.dataset.row, 10);
      const c = parseInt(sq.dataset.col, 10);
      const p = state.board[r][c];
      
      sq.classList.remove('selected', 'legal-move', 'legal-capture', 'in-check');
      // Remove only the piece span, leaving coord labels intact.
      const oldPiece = sq.querySelector('.chess-piece');
      if (oldPiece) oldPiece.remove();
      
      if (p) {
        const span = document.createElement('span');
        span.className = 'chess-piece ' + p.color;
        span.textContent = PIECE_GLYPHS[p.color + p.type];
        sq.appendChild(span);
      }
      
      // Highlight in-check king
      if (p && p.type === 'k' && isInCheck(state.board, p.color)) {
        sq.classList.add('in-check');
      }
    });
    
    // Highlight selected piece + its legal moves
    if (state.selected) {
      const selSq = squares[state.selected.row * 8 + state.selected.col];
      if (selSq) selSq.classList.add('selected');
      for (const m of state.legalMoves) {
        const tSq = squares[m.row * 8 + m.col];
        if (!tSq) continue;
        if (state.board[m.row][m.col] || m.special === 'en-passant') {
          tSq.classList.add('legal-capture');
        } else {
          tSq.classList.add('legal-move');
        }
      }
    }
    
    // Update status
    const statusEl = root.querySelector('[data-role="status"]');
    
    if (state.gameOver === 'checkmate-w') {
      statusEl.textContent = t.blackWins;
      statusEl.className = 'chess-status game-over';
    } else if (state.gameOver === 'checkmate-b') {
      statusEl.textContent = t.whiteWins;
      statusEl.className = 'chess-status game-over';
    } else if (state.gameOver === 'stalemate') {
      statusEl.textContent = t.stalemate;
      statusEl.className = 'chess-status game-over';
    } else {
      const turnText = state.turn === 'w' ? t.whiteTurn : t.blackTurn;
      const checkText = isInCheck(state.board, state.turn) ? ' — ' + t.inCheck : '';
      statusEl.textContent = turnText + checkText;
      statusEl.className = 'chess-status' + (checkText ? ' in-check' : '');
    }
  }
  
  // ─── Interaction ───────────────────────────────────────
  
  function handleSquareClick(r, c) {
    if (state.gameOver) return;
    
    // If a piece is currently selected and the user clicks a legal-move square, make the move.
    if (state.selected) {
      const move = state.legalMoves.find(m => m.row === r && m.col === c);
      if (move) {
        makeMove(state.selected.row, state.selected.col, r, c, move.special);
        return;
      }
    }
    
    // Otherwise: select clicked piece if it belongs to current player.
    const p = state.board[r][c];
    if (p && p.color === state.turn) {
      state.selected = { row: r, col: c };
      state.legalMoves = legalMoves(state.board, r, c, state.castlingRights, state.enPassantTarget);
      render();
    } else if (p && p.color !== state.turn) {
      // Allow inspecting opponent pieces too (shows their rules) but no move highlights.
      state.selected = { row: r, col: c };
      state.legalMoves = [];  // can't move opponent's piece
      render();
    } else {
      state.selected = null;
      state.legalMoves = [];
      render();
    }
  }
  
  function makeMove(fromR, fromC, toR, toC, special) {
    // Snapshot for undo
    const snapshot = {
      board: state.board.map(r => r.slice()),
      turn: state.turn,
      castlingRights: { ...state.castlingRights },
      enPassantTarget: state.enPassantTarget,
    };
    state.moveHistory.push(snapshot);
    
    const result = applyMove(state.board, fromR, fromC, toR, toC, special, state.castlingRights);
    state.board = result.newBoard;
    state.castlingRights = result.newCastlingRights;
    state.enPassantTarget = result.newEnPassantTarget;
    state.turn = state.turn === 'w' ? 'b' : 'w';
    state.selected = null;
    state.legalMoves = [];
    
    // Check for game end
    if (!hasAnyLegalMove(state.board, state.turn, state.castlingRights, state.enPassantTarget)) {
      if (isInCheck(state.board, state.turn)) {
        state.gameOver = 'checkmate-' + state.turn;
      } else {
        state.gameOver = 'stalemate';
      }
    }
    
    render();
    if (!state.gameOver) analyze(toFEN(state));
    else renderSf();
  }
  
  function undoMove() {
    if (state.moveHistory.length === 0) return;
    const prev = state.moveHistory.pop();
    state.board = prev.board;
    state.turn = prev.turn;
    state.castlingRights = prev.castlingRights;
    state.enPassantTarget = prev.enPassantTarget;
    state.selected = null;
    state.legalMoves = [];
    state.gameOver = null;
    render();
    analyze(toFEN(state));
  }
  
  function resetGame() {
    state = {
      board: initialBoard(),
      turn: 'w',
      selected: null,
      legalMoves: [],
      castlingRights: { wK: true, wQ: true, bK: true, bQ: true },
      enPassantTarget: null,
      moveHistory: [],
      gameOver: null,
    };
    render();
    analyze(toFEN(state));
  }
  
  // ─── Bootstrap ─────────────────────────────────────────
  buildBoardDOM();
  render();
  initStockfish();
});

// ─── Bilingual strings ────────────────────────────────────
const STRINGS = {
  en: {
    undo: 'Undo',
    reset: 'Reset',
    whiteTurn: "White to move",
    blackTurn: "Black to move",
    inCheck: 'in check',
    whiteWins: 'White wins by checkmate',
    blackWins: 'Black wins by checkmate',
    stalemate: 'Stalemate — draw',
    sfLoading: 'Loading Stockfish…',
    sfReady: 'Stockfish ready',
    sfThinking: 'Stockfish thinking…',
    sfBestMove: 'best',
    sfDepth: 'depth',
    sfMate: 'mate in',
    sfEvalLabel: 'eval',
    sfFailed: 'Stockfish failed to load',
  },
  zh: {
    undo: '悔棋',
    reset: '重新开始',
    whiteTurn: '白方走子',
    blackTurn: '黑方走子',
    inCheck: '被将军',
    whiteWins: '白方将杀获胜',
    blackWins: '黑方将杀获胜',
    stalemate: '逼和——和棋',
    sfLoading: 'Stockfish 加载中…',
    sfReady: 'Stockfish 就绪',
    sfThinking: 'Stockfish 思考中…',
    sfBestMove: '最佳着法',
    sfDepth: '深度',
    sfMate: '将杀',
    sfEvalLabel: '评估',
    sfFailed: 'Stockfish 加载失败',
  },
};

})();
