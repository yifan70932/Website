/* ============================================================
   yifanova.com — interactive chess board (chess.js)
   ------------------------------------------------------------
   A single chess board widget that:
   - Displays the standard 8×8 starting position.
   - Highlights legal moves when the user clicks a piece.
   - Shows a description of the selected piece's movement rules.
   - Lets two humans play out a full game (no AI).
   - Supports check, checkmate, stalemate, and basic draws.
   - Bilingual UI (English / Chinese) via lang attribute.

   This is designed to teach the rules visually, not to be a
   competitive playing surface. Castling, en passant, and pawn
   promotion are implemented; threefold repetition and the
   fifty-move rule are not (kept simple).
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
        sq.setAttribute('aria-label', squareLabel(r, c));
        sq.addEventListener('click', () => handleSquareClick(r, c));
        boardDiv.appendChild(sq);
      }
    }
    
    const info = document.createElement('div');
    info.className = 'chess-info';
    info.innerHTML = `
      <div class="chess-status" data-role="status"></div>
      <div class="chess-rule" data-role="rule">
        <p class="chess-rule-hint">${t.hint}</p>
      </div>
      <div class="chess-controls">
        <button type="button" data-role="undo">${t.undo}</button>
        <button type="button" data-role="reset">${t.reset}</button>
      </div>
    `;
    
    wrap.appendChild(boardDiv);
    wrap.appendChild(info);
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
      sq.innerHTML = '';
      
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
    
    // Update status + rule panel
    const statusEl = root.querySelector('[data-role="status"]');
    const ruleEl = root.querySelector('[data-role="rule"]');
    
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
    
    // Rule description
    if (state.selected) {
      const p = state.board[state.selected.row][state.selected.col];
      if (p) {
        const ruleData = t.rules[p.type];
        ruleEl.innerHTML = `
          <h4>${PIECE_GLYPHS[p.color + p.type]} ${ruleData.name}</h4>
          <p>${ruleData.desc}</p>
        `;
      }
    } else {
      ruleEl.innerHTML = `<p class="chess-rule-hint">${t.hint}</p>`;
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
  }
  
  // ─── Bootstrap ─────────────────────────────────────────
  buildBoardDOM();
  render();
});

// ─── Bilingual strings ────────────────────────────────────
const STRINGS = {
  en: {
    hint: 'Click any piece to see how it moves. Click a highlighted square to play that move. Two players share the board.',
    undo: 'Undo',
    reset: 'Reset',
    whiteTurn: "White to move",
    blackTurn: "Black to move",
    inCheck: 'in check',
    whiteWins: 'White wins by checkmate',
    blackWins: 'Black wins by checkmate',
    stalemate: 'Stalemate — draw',
    rules: {
      p: { name: 'Pawn', desc: 'Moves forward one square; on its first move it may advance two. Captures diagonally forward, never straight ahead. Reaching the far rank, it promotes (this widget auto-promotes to a queen). Special: <em>en passant</em> capture of an adjacent pawn that has just moved two squares.' },
      n: { name: 'Knight', desc: 'Moves in an L-shape: two squares along one axis and one along the other. Uniquely, the knight can jump over other pieces.' },
      b: { name: 'Bishop', desc: 'Moves any number of squares diagonally. Cannot jump over pieces. Each side has one light-square bishop and one dark-square bishop, and these two never trade squares with each other.' },
      r: { name: 'Rook', desc: 'Moves any number of squares orthogonally — along ranks or files. Cannot jump. Participates in castling with the king.' },
      q: { name: 'Queen', desc: 'Moves any number of squares orthogonally or diagonally — combining rook and bishop. The most powerful piece on the board, but not the goal of the game.' },
      k: { name: 'King', desc: 'Moves one square in any direction. Cannot move to a square attacked by an enemy piece. May castle once per game with an unmoved rook if no piece sits between them, the king is not in check, and does not pass through or land on an attacked square. Checkmating the king ends the game.' },
    },
  },
  zh: {
    hint: '点击任意棋子查看它的走法；点击高亮格落子。两位玩家共用一个棋盘。',
    undo: '悔棋',
    reset: '重新开始',
    whiteTurn: '白方走子',
    blackTurn: '黑方走子',
    inCheck: '被将军',
    whiteWins: '白方将杀获胜',
    blackWins: '黑方将杀获胜',
    stalemate: '逼和——和棋',
    rules: {
      p: { name: '兵 (Pawn)', desc: '每次向前一格；首次走子可前进两格。斜向前一格吃子，不能沿直线吃子。到达对方底线时升变（此处自动升变为后）。特殊走法：<em>吃过路兵</em>——对方相邻一兵刚走两格时，可以斜前吃之。' },
      n: { name: '马 (Knight)', desc: '走"L"形——一个方向两格、垂直方向一格。马是棋盘上唯一可以越过其他棋子的子。' },
      b: { name: '象 (Bishop)', desc: '沿斜线任意距离移动，不能越子。每方有一个白格象、一个黑格象，两象终生不会换格。' },
      r: { name: '车 (Rook)', desc: '沿横线或竖线任意距离移动，不能越子。参与王车易位。' },
      q: { name: '后 (Queen)', desc: '沿横线、竖线或斜线任意距离移动，相当于车与象的组合。是棋盘上最强的子，但不是游戏的目标。' },
      k: { name: '王 (King)', desc: '向任一方向走一格。不能走到对方控制的格上。每局可与未走过的车做一次"王车易位"，前提是它们之间无子、王不在被将军中、王不会经过或停在受攻击格上。王被将杀即为终局。' },
    },
  },
};

})();
