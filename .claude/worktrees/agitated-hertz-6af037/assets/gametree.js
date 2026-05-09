/* ============================================================
   yifanova.com — interactive minimax game tree
   ------------------------------------------------------------
   3-level ternary tree (27 leaves) with on-demand expansion.

   Default view: root + L1 nodes visible; deeper subtrees show
   as "..." stubs. Click a stub to expand. Click "Demonstrate
   backward induction" to expand all and animate from leaves up.

   Animation highlight uses ink-black (matches chess pieces /
   the ink token in the design system); the final static
   "chosen branch" colour remains forest green.

   Pure SVG + vanilla JS. No dependencies.
   ============================================================ */

(function() {
"use strict";

const TXT = {
  en: {
    instruction: 'A schematic chess game tree with three plies and branching factor three. Each level’s subtrees are collapsed under "…" by default — click any stub to expand it, or press Demonstrate to expand the whole tree and animate the propagation of values from leaves to root.',
    btnPlay: 'Demonstrate backward induction',
    btnReplay: 'Replay',
    legendW: 'White to move (max)',
    legendB: 'Black to move (min)',
    legendWin: 'White wins (+1)',
    legendDraw: 'draw (0)',
    legendLoss: 'Black wins (−1)',
    legendChosen: 'chosen branch',
    legendStub: 'collapsed subtree',
    rootResult: (v) => v === 1 ? 'Root value: +1 — White can force a win.' :
                       v === -1 ? 'Root value: −1 — Black can force a win.' :
                       'Root value: 0 — both sides can force at least a draw.',
  },
  zh: {
    instruction: '一棵三层、分支因子为三的示意博弈树。每一层的子树默认折叠为"…"，点击任一折叠节点可展开；或点击"演示"按钮，自动展开整棵树并播放从叶子到根的逆向归纳动画。',
    btnPlay: '演示逆向归纳',
    btnReplay: '重播',
    legendW: '白方走（取最大）',
    legendB: '黑方走（取最小）',
    legendWin: '白胜（+1）',
    legendDraw: '和棋（0）',
    legendLoss: '黑胜（−1）',
    legendChosen: '选中分支',
    legendStub: '折叠的子树',
    rootResult: (v) => v === 1 ? '根值：+1 —— 白方可强制取胜。' :
                       v === -1 ? '根值：−1 —— 黑方可强制取胜。' :
                       '根值：0 —— 双方至少都能强制和棋。',
  }
};

const DEPTH = 3;
const BRANCH = 3;

function buildTree(depth, branch, leafValues) {
  const nodes = [];
  let id = 0;
  function make(level, parentId) {
    const n = {
      id: id++, level, parentId,
      children: [],
      isLeaf: level === depth,
      isMax: level % 2 === 0,
      value: null,
      chosenChildId: null,
      solved: false,
      // expanded: should this node's children be drawn?
      // Default: only the root is expanded — the root's L1 children show,
      // but nothing below them.
      expanded: level === 0,
    };
    nodes.push(n);
    if (!n.isLeaf) {
      for (let i = 0; i < branch; i++) {
        const c = make(level + 1, n.id);
        n.children.push(c.id);
      }
    }
    return n;
  }
  make(0, null);

  // Assign leaf values in DFS-leaf order (which is left-to-right after layout)
  let li = 0;
  for (const n of nodes) {
    if (n.isLeaf) {
      n.value = leafValues[li++];
      n.solved = true;
    }
  }
  return nodes;
}

function solveOne(nodes, nodeId) {
  const n = nodes[nodeId];
  if (n.solved) return;
  const childVals = n.children.map(cid => nodes[cid].value);
  let best = childVals[0], bestIdx = 0;
  for (let i = 1; i < childVals.length; i++) {
    if (n.isMax ? childVals[i] > best : childVals[i] < best) {
      best = childVals[i]; bestIdx = i;
    }
  }
  n.value = best;
  n.chosenChildId = n.children[bestIdx];
  n.solved = true;
}

/**
 * Layout — only positions nodes that are *visible*.
 * A node is visible if itself and all its ancestors are expanded.
 *
 * Returns the visible-leaf list (in left-to-right order at the bottom).
 * Uses a "tidy tree" approach: leaves get evenly spaced x-positions
 * along the available width; internal nodes are centered above the
 * visible portion of their subtree.
 */
function layout(nodes, width, height) {
  const padding = { top: 30, bottom: 30, left: 30, right: 30 };
  const innerW = width - padding.left - padding.right;
  const innerH = height - padding.top - padding.bottom;

  // Determine visibility: a node is visible if its parent is expanded
  // (root is always visible). A *stub* is a non-leaf node that is itself
  // not expanded — drawn as a single small "…" badge instead of subtree.
  for (const n of nodes) {
    n.visible = false;
    n.isStub = false;
  }
  function markVisible(id) {
    const n = nodes[id];
    n.visible = true;
    if (!n.isLeaf) {
      if (n.expanded) {
        for (const cid of n.children) markVisible(cid);
      } else {
        n.isStub = true;  // visible but its children aren't drawn
      }
    }
  }
  markVisible(0);

  // The "frontier" is the bottom edge of the visible tree:
  // visible leaves OR visible stubs (which act as bottom-of-subtree markers).
  // These get evenly spaced x-positions.
  const frontier = nodes.filter(n => n.visible && (n.isLeaf || n.isStub));
  // We need them in DFS-left-to-right order to lay them out correctly.
  // Walk the visible tree DFS to collect frontier in order.
  const ordered = [];
  function dfs(id) {
    const n = nodes[id];
    if (!n.visible) return;
    if (n.isLeaf || n.isStub) {
      ordered.push(n);
    } else {
      for (const cid of n.children) dfs(cid);
    }
  }
  dfs(0);

  // Each frontier node gets an x slot
  ordered.forEach((n, i) => {
    n.x = padding.left + (innerW * (i + 0.5)) / ordered.length;
  });

  // Find max visible level for vertical scaling
  const maxLevel = Math.max(...nodes.filter(n => n.visible).map(n => n.level));
  const levelGap = maxLevel === 0 ? 0 : innerH / maxLevel;

  for (const n of nodes) {
    if (!n.visible) continue;
    n.y = padding.top + n.level * levelGap;
  }

  // Internal non-stub visible nodes: center on visible children
  // Walk bottom-up over visible internal expanded nodes
  for (let lv = maxLevel - 1; lv >= 0; lv--) {
    const here = nodes.filter(n => n.visible && !n.isLeaf && !n.isStub && n.level === lv);
    for (const n of here) {
      const xs = n.children.map(cid => nodes[cid].x).filter(x => x !== undefined);
      if (xs.length) {
        n.x = xs.reduce((a, b) => a + b, 0) / xs.length;
      }
    }
  }
}

class GameTree {
  constructor(containerId, opts = {}) {
    this.container = typeof containerId === 'string'
      ? document.getElementById(containerId)
      : containerId;
    this.lang = opts.lang || 'en';
    this.t = TXT[this.lang];
    this.initialLeafValues = opts.leafValues || [
      // 27 leaves; computes to root = +1 (White can force a win).
      // Inner values: L2 = [1,−1,1, 1,0,0, 1,1,1], L1 = [−1,0,1].
      -1, 0, 1,   -1,-1,-1,   -1, 1, 0,
       1,-1, 0,   -1, 0,-1,    0, 0, 0,
       0, 0, 1,    1, 0, 0,   -1,-1, 1,
    ];
    this.svgWidth = opts.width || 870;
    this.svgHeight = opts.height || 320;
    this.animating = false;
    this.render();
  }

  reset() {
    this.nodes = buildTree(DEPTH, BRANCH, this.initialLeafValues);
    layout(this.nodes, this.svgWidth, this.svgHeight);
    this.draw();
    this.resultEl.textContent = '';
    this.resultEl.classList.remove('shown');
    this.btn.textContent = this.t.btnPlay;
    this.btn.disabled = false;
    this.animating = false;
  }

  expandAll() {
    for (const n of this.nodes) {
      if (!n.isLeaf) n.expanded = true;
    }
    layout(this.nodes, this.svgWidth, this.svgHeight);
  }

  expand(nodeId) {
    if (this.animating) return;
    const n = this.nodes[nodeId];
    if (n.isLeaf || n.expanded) return;
    n.expanded = true;
    layout(this.nodes, this.svgWidth, this.svgHeight);
    this.draw();
  }

  render() {
    this.container.innerHTML = '';
    this.container.classList.add('gametree-container');

    const caption = document.createElement('p');
    caption.className = 'gametree-instruction';
    caption.textContent = this.t.instruction;
    this.container.appendChild(caption);

    this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    this.svg.setAttribute('viewBox', `0 0 ${this.svgWidth} ${this.svgHeight}`);
    this.svg.setAttribute('class', 'gametree-svg');
    this.svg.setAttribute('role', 'img');
    this.svg.setAttribute('aria-label', this.t.instruction);
    this.container.appendChild(this.svg);

    const controls = document.createElement('div');
    controls.className = 'gametree-controls';

    this.btn = document.createElement('button');
    this.btn.className = 'gametree-btn-primary';
    this.btn.onclick = () => {
      if (this.animating) return;
      // If already solved, reset and replay
      if (this.nodes[0].solved) {
        this.reset();
        setTimeout(() => this.runDemonstration(), 200);
      } else {
        this.runDemonstration();
      }
    };
    controls.appendChild(this.btn);

    this.resultEl = document.createElement('span');
    this.resultEl.className = 'gametree-result';
    controls.appendChild(this.resultEl);

    this.container.appendChild(controls);

    const legend = document.createElement('div');
    legend.className = 'gametree-legend';
    legend.innerHTML = `
      <span class="leg-item"><span class="leg-circle leg-w"></span>${this.t.legendW}</span>
      <span class="leg-item"><span class="leg-circle leg-b"></span>${this.t.legendB}</span>
      <span class="leg-item"><span class="leg-stub-marker">…</span>${this.t.legendStub}</span>
      <span class="leg-item"><span class="leg-swatch leg-win"></span>${this.t.legendWin}</span>
      <span class="leg-item"><span class="leg-swatch leg-draw"></span>${this.t.legendDraw}</span>
      <span class="leg-item"><span class="leg-swatch leg-loss"></span>${this.t.legendLoss}</span>
      <span class="leg-item"><span class="leg-line leg-chosen"></span>${this.t.legendChosen}</span>
    `;
    this.container.appendChild(legend);

    this.reset();
  }

  draw(highlightNodeId = null) {
    while (this.svg.firstChild) this.svg.removeChild(this.svg.firstChild);
    const NS = 'http://www.w3.org/2000/svg';

    // Edges: drawn from each visible expanded internal node to each of
    // its children (which are themselves visible).
    for (const n of this.nodes) {
      if (!n.visible || n.isLeaf || n.isStub) continue;
      for (const cid of n.children) {
        const c = this.nodes[cid];
        if (!c.visible) continue;
        const line = document.createElementNS(NS, 'line');
        line.setAttribute('x1', n.x); line.setAttribute('y1', n.y);
        line.setAttribute('x2', c.x); line.setAttribute('y2', c.y);
        let cls = 'edge';
        if (n.solved) {
          cls += (n.chosenChildId === cid) ? ' edge-chosen' : ' edge-unchosen';
        }
        // Active animation: ink-black pulse along the chosen edge of the
        // currently-highlighted node
        if (highlightNodeId !== null && n.id === highlightNodeId &&
            n.chosenChildId === cid) {
          cls += ' edge-pulse';
        }
        line.setAttribute('class', cls);
        this.svg.appendChild(line);
      }
    }

    // Nodes
    for (const n of this.nodes) {
      if (!n.visible) continue;
      const g = document.createElementNS(NS, 'g');
      g.setAttribute('transform', `translate(${n.x},${n.y})`);

      if (n.isLeaf) {
        const r = document.createElementNS(NS, 'rect');
        r.setAttribute('x', -10); r.setAttribute('y', -9);
        r.setAttribute('width', 20); r.setAttribute('height', 18);
        r.setAttribute('rx', 2);
        const valCls = n.value > 0 ? 'leaf-win' : (n.value < 0 ? 'leaf-loss' : 'leaf-draw');
        r.setAttribute('class', `node-leaf ${valCls}`);
        g.appendChild(r);

        const t = document.createElementNS(NS, 'text');
        t.setAttribute('text-anchor', 'middle');
        t.setAttribute('dominant-baseline', 'central');
        t.setAttribute('class', 'node-label-leaf');
        t.textContent = n.value > 0 ? '+1' : (n.value < 0 ? '−1' : '0');
        g.appendChild(t);
      } else {
        // Internal node — circle
        const c = document.createElementNS(NS, 'circle');
        c.setAttribute('r', 13);
        let cls = n.isMax ? 'node-max' : 'node-min';
        if (n.id === highlightNodeId) cls += ' node-highlight';
        if (n.solved) cls += ' node-solved';
        if (n.isStub) cls += ' node-stub';
        c.setAttribute('class', cls);
        g.appendChild(c);

        // Letter inside (W / B)
        const inside = document.createElementNS(NS, 'text');
        inside.setAttribute('text-anchor', 'middle');
        inside.setAttribute('dominant-baseline', 'central');
        inside.setAttribute('class', n.isMax ? 'node-letter-max' : 'node-letter-min');
        inside.textContent = n.isMax ? 'W' : 'B';
        g.appendChild(inside);

        // Stub indicator: ellipsis below
        if (n.isStub) {
          const dots = document.createElementNS(NS, 'text');
          dots.setAttribute('text-anchor', 'middle');
          dots.setAttribute('y', 28);
          dots.setAttribute('class', 'node-stub-dots');
          dots.textContent = '…';
          g.appendChild(dots);

          // Click handler to expand
          g.style.cursor = 'pointer';
          g.addEventListener('click', () => this.expand(n.id));
          // hover affordance: bigger hit target
          const hit = document.createElementNS(NS, 'circle');
          hit.setAttribute('r', 22);
          hit.setAttribute('class', 'node-hit');
          g.insertBefore(hit, c);
        }

        // Value label above (only for non-stub internal nodes — stubs
        // don't have values yet because their subtrees aren't expanded)
        if (!n.isStub) {
          const v = document.createElementNS(NS, 'text');
          v.setAttribute('x', 0);
          v.setAttribute('y', -19);
          v.setAttribute('text-anchor', 'middle');
          let vcls = 'node-value';
          if (n.solved) {
            vcls += ' ' + (n.value > 0 ? 'val-win' : (n.value < 0 ? 'val-loss' : 'val-draw'));
          } else {
            vcls += ' val-unsolved';
          }
          v.setAttribute('class', vcls);
          v.textContent = n.solved
            ? (n.value > 0 ? '+1' : (n.value < 0 ? '−1' : '0'))
            : '?';
          g.appendChild(v);
        }
      }

      this.svg.appendChild(g);
    }
  }

  async runDemonstration() {
    this.animating = true;
    this.btn.disabled = true;
    this.btn.textContent = this.lang === 'zh' ? '演示中…' : 'Animating…';

    // Phase 1: expand the whole tree (with brief pause for users to see it grow)
    this.expandAll();
    this.draw();
    await sleep(700);

    // Phase 2: solve bottom-up, level by level, animating each node
    const STEP_DELAY = 110;
    const LEVEL_PAUSE = 550;
    const HIGHLIGHT_HOLD = 260;

    const levelLists = {};
    for (const n of this.nodes) {
      if (n.isLeaf) continue;
      (levelLists[n.level] = levelLists[n.level] || []).push(n);
    }
    const internalLevels = Object.keys(levelLists)
      .map(Number).sort((a, b) => b - a);

    for (const lv of internalLevels) {
      const levelNodes = levelLists[lv].sort((a, b) => a.x - b.x);
      for (const n of levelNodes) {
        solveOne(this.nodes, n.id);
        this.draw(n.id);
        await sleep(HIGHLIGHT_HOLD);
        this.draw();
        await sleep(STEP_DELAY);
      }
      await sleep(LEVEL_PAUSE);
    }

    const rootValue = this.nodes[0].value;
    this.resultEl.textContent = this.t.rootResult(rootValue);
    this.resultEl.classList.add('shown');
    this.btn.textContent = this.t.btnReplay;
    this.btn.disabled = false;
    this.animating = false;
  }
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

window.GameTree = GameTree;
})();
