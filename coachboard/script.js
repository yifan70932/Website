const pitch = document.getElementById("pitch");
const playersLayer = document.getElementById("playersLayer");
const canvas = document.getElementById("drawingCanvas");
const ctx = canvas.getContext("2d");

const formationSelect = document.getElementById("formationSelect");
const formationLabel = document.getElementById("formationLabel");
const noteInput = document.getElementById("noteInput");
const notePreview = document.getElementById("notePreview");
const resetBtn = document.getElementById("resetBtn");
const exportBtn = document.getElementById("exportBtn");
const clearDrawingsBtn = document.getElementById("clearDrawingsBtn");
const flipBoardBtn = document.getElementById("flipBoardBtn");
const toggleHome = document.getElementById("toggleHome");
const toggleAway = document.getElementById("toggleAway");
const toolButtons = document.querySelectorAll(".tool");

let activeTool = "move";
let activePlayer = null;
let drawing = false;
let startPoint = null;
let drawings = [];
let flipped = false;

const formations = {
  "433": {
    label: "4-3-3",
    home: [[8, 50], [20, 18], [20, 39], [20, 61], [20, 82], [39, 30], [35, 50], [39, 70], [60, 22], [66, 50], [60, 78]],
    away: [[92, 50], [80, 18], [80, 39], [80, 61], [80, 82], [61, 30], [65, 50], [61, 70], [40, 22], [34, 50], [40, 78]]
  },
  "442": {
    label: "4-4-2",
    home: [[8, 50], [22, 18], [20, 39], [20, 61], [22, 82], [43, 18], [39, 39], [39, 61], [43, 82], [62, 40], [62, 60]],
    away: [[92, 50], [78, 18], [80, 39], [80, 61], [78, 82], [57, 18], [61, 39], [61, 61], [57, 82], [38, 40], [38, 60]]
  },
  "4231": {
    label: "4-2-3-1",
    home: [[8, 50], [21, 18], [20, 39], [20, 61], [21, 82], [36, 42], [36, 58], [53, 25], [53, 50], [53, 75], [68, 50]],
    away: [[92, 50], [79, 18], [80, 39], [80, 61], [79, 82], [64, 42], [64, 58], [47, 25], [47, 50], [47, 75], [32, 50]]
  },
  "352": {
    label: "3-5-2",
    home: [[8, 50], [21, 30], [18, 50], [21, 70], [42, 15], [36, 35], [34, 50], [36, 65], [42, 85], [62, 40], [62, 60]],
    away: [[92, 50], [79, 30], [82, 50], [79, 70], [58, 15], [64, 35], [66, 50], [64, 65], [58, 85], [38, 40], [38, 60]]
  }
};

function createPlayers() {
  playersLayer.innerHTML = "";
  ["home", "away"].forEach(team => {
    for (let i = 1; i <= 11; i += 1) {
      const player = document.createElement("button");
      player.className = `player ${team}`;
      player.type = "button";
      player.textContent = i;
      player.dataset.team = team;
      player.dataset.index = i - 1;
      player.setAttribute("aria-label", `${team} player ${i}`);
      playersLayer.appendChild(player);
    }
  });
}

function applyFormation(key) {
  if (key === "custom") return;
  const formation = formations[key];
  formationLabel.textContent = formation.label;

  document.querySelectorAll(".player").forEach(player => {
    const team = player.dataset.team;
    const index = Number(player.dataset.index);
    const point = formation[team][index];
    setPlayerPosition(player, point[0], point[1]);
  });
}

function setPlayerPosition(player, x, y) {
  player.style.left = `${x}%`;
  player.style.top = `${y}%`;
  player.dataset.x = String(x);
  player.dataset.y = String(y);
}

function getPitchPoint(event) {
  const rect = pitch.getBoundingClientRect();
  const pointer = event.touches ? event.touches[0] : event;
  return {
    x: Math.max(0, Math.min(100, ((pointer.clientX - rect.left) / rect.width) * 100)),
    y: Math.max(0, Math.min(100, ((pointer.clientY - rect.top) / rect.height) * 100)),
  };
}

function resizeCanvas() {
  const rect = pitch.getBoundingClientRect();
  const scale = window.devicePixelRatio || 1;
  canvas.width = rect.width * scale;
  canvas.height = rect.height * scale;
  canvas.style.width = `${rect.width}px`;
  canvas.style.height = `${rect.height}px`;
  ctx.setTransform(scale, 0, 0, scale, 0, 0);
  redraw();
}

function percentToPixels(point) {
  const rect = pitch.getBoundingClientRect();
  return {
    x: (point.x / 100) * rect.width,
    y: (point.y / 100) * rect.height
  };
}

function drawShape(shape, preview = false) {
  const from = percentToPixels(shape.from);
  const to = percentToPixels(shape.to);

  ctx.save();
  ctx.lineWidth = preview ? 4 : 5;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.strokeStyle = preview ? "rgba(255,255,255,0.7)" : "rgba(255,255,255,0.95)";

  ctx.beginPath();
  ctx.moveTo(from.x, from.y);
  ctx.lineTo(to.x, to.y);
  ctx.stroke();

  if (shape.type === "arrow") {
    const angle = Math.atan2(to.y - from.y, to.x - from.x);
    const size = 16;
    ctx.beginPath();
    ctx.moveTo(to.x, to.y);
    ctx.lineTo(to.x - size * Math.cos(angle - Math.PI / 6), to.y - size * Math.sin(angle - Math.PI / 6));
    ctx.lineTo(to.x - size * Math.cos(angle + Math.PI / 6), to.y - size * Math.sin(angle + Math.PI / 6));
    ctx.closePath();
    ctx.fillStyle = ctx.strokeStyle;
    ctx.fill();
  }
  ctx.restore();
}

function redraw(previewShape = null) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawings.forEach(shape => drawShape(shape));
  if (previewShape) drawShape(previewShape, true);
}

function updateTool(tool) {
  activeTool = tool;
  toolButtons.forEach(button => button.classList.toggle("active", button.dataset.tool === tool));
  canvas.style.pointerEvents = tool === "move" ? "none" : "auto";
}

function updateTeamVisibility() {
  document.querySelectorAll(".player.home").forEach(p => p.classList.toggle("hidden", !toggleHome.checked));
  document.querySelectorAll(".player.away").forEach(p => p.classList.toggle("hidden", !toggleAway.checked));
}

function resetBoard() {
  flipped = false;
  drawings = [];
  formationSelect.value = "433";
  noteInput.value = "";
  notePreview.textContent = "Add a coach note from the control panel.";
  applyFormation("433");
  updateTeamVisibility();
  redraw();
}

function flipBoard() {
  flipped = !flipped;
  document.querySelectorAll(".player").forEach(player => {
    const x = Number(player.dataset.x);
    const y = Number(player.dataset.y);
    setPlayerPosition(player, 100 - x, 100 - y);
  });

  drawings = drawings.map(shape => ({
    ...shape,
    from: { x: 100 - shape.from.x, y: 100 - shape.from.y },
    to: { x: 100 - shape.to.x, y: 100 - shape.to.y }
  }));
  redraw();
}

playersLayer.addEventListener("pointerdown", event => {
  const player = event.target.closest(".player");
  if (!player || activeTool !== "move") return;
  activePlayer = player;
  player.setPointerCapture(event.pointerId);
});

playersLayer.addEventListener("pointermove", event => {
  if (!activePlayer || activeTool !== "move") return;
  const point = getPitchPoint(event);
  setPlayerPosition(activePlayer, point.x, point.y);
  formationSelect.value = "custom";
  formationLabel.textContent = "Custom";
});

playersLayer.addEventListener("pointerup", event => {
  if (!activePlayer) return;
  activePlayer.releasePointerCapture(event.pointerId);
  activePlayer = null;
});

pitch.addEventListener("pointerdown", event => {
  if (activeTool === "move") return;
  drawing = true;
  startPoint = getPitchPoint(event);
});

pitch.addEventListener("pointermove", event => {
  if (!drawing || activeTool === "move") return;
  const current = getPitchPoint(event);
  redraw({ type: activeTool, from: startPoint, to: current });
});

pitch.addEventListener("pointerup", event => {
  if (!drawing || activeTool === "move") return;
  const endPoint = getPitchPoint(event);
  drawings.push({ type: activeTool, from: startPoint, to: endPoint });
  drawing = false;
  startPoint = null;
  redraw();
});

toolButtons.forEach(button => {
  button.addEventListener("click", () => updateTool(button.dataset.tool));
});

formationSelect.addEventListener("change", event => applyFormation(event.target.value));

noteInput.addEventListener("input", event => {
  const value = event.target.value.trim();
  notePreview.textContent = value || "Add a coach note from the control panel.";
});

toggleHome.addEventListener("change", updateTeamVisibility);
toggleAway.addEventListener("change", updateTeamVisibility);
clearDrawingsBtn.addEventListener("click", () => {
  drawings = [];
  redraw();
});
flipBoardBtn.addEventListener("click", flipBoard);
resetBtn.addEventListener("click", resetBoard);

exportBtn.addEventListener("click", async () => {
  await exportBoardAsPng();
});

async function exportBoardAsPng() {
  const area = document.getElementById("captureArea");
  const rect = area.getBoundingClientRect();

  const svgData = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${rect.width}" height="${rect.height}">
      <foreignObject width="100%" height="100%">
        ${new XMLSerializer().serializeToString(area.cloneNode(true))}
      </foreignObject>
    </svg>
  `;

  const blob = new Blob([svgData], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const image = new Image();

  image.onload = () => {
    const exportCanvas = document.createElement("canvas");
    exportCanvas.width = rect.width * 2;
    exportCanvas.height = rect.height * 2;
    const exportCtx = exportCanvas.getContext("2d");
    exportCtx.scale(2, 2);
    exportCtx.drawImage(image, 0, 0);
    URL.revokeObjectURL(url);

    const link = document.createElement("a");
    link.download = "soccer-coach-board.png";
    link.href = exportCanvas.toDataURL("image/png");
    link.click();
  };

  image.src = url;
}

window.addEventListener("resize", resizeCanvas);

createPlayers();
applyFormation("433");
updateTool("move");
updateTeamVisibility();
resizeCanvas();
