const pitch = document.getElementById("pitch");
const playersLayer = document.getElementById("playersLayer");
const canvas = document.getElementById("drawingCanvas");
const ctx = canvas.getContext("2d");
const ball = document.getElementById("ball");

const formationSelect = document.getElementById("formationSelect");
const fieldViewSelect = document.getElementById("fieldViewSelect");
const formationLabel = document.getElementById("formationLabel");
const noteInput = document.getElementById("noteInput");
const notePreview = document.getElementById("notePreview");
const resetBtn = document.getElementById("resetBtn");
const exportBtn = document.getElementById("exportBtn");
const fullscreenBtn = document.getElementById("fullscreenBtn");
const boardFullscreenBtn = document.getElementById("boardFullscreenBtn");
const captureArea = document.getElementById("captureArea");
const clearDrawingsBtn = document.getElementById("clearDrawingsBtn");
const flipBoardBtn = document.getElementById("flipBoardBtn");
const toggleHome = document.getElementById("toggleHome");
const toggleAway = document.getElementById("toggleAway");
const homeColor = document.getElementById("homeColor");
const awayColor = document.getElementById("awayColor");
const drawingColor = document.getElementById("drawingColor");
const ballColor = document.getElementById("ballColor");
const showBallBtn = document.getElementById("showBallBtn");
const hideBallBtn = document.getElementById("hideBallBtn");
const toolButtons = document.querySelectorAll(".tool");

let activeTool = "move";
let activePlayer = null;
let activeObject = null;
let drawing = false;
let startPoint = null;
let drawings = [];
let currentFieldView = "full";

const fieldLabels = {
  full: "Full Field",
  "attacking-half": "Attacking Half",
  "left-corner": "Left Corner",
  "right-corner": "Right Corner",
  "free-kick-zone": "Free Kick Zone"
};

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
  },
  "corner": {
    label: "Set piece shape",
    home: [[11, 48], [32, 22], [34, 35], [39, 47], [32, 60], [42, 72], [55, 20], [58, 38], [61, 55], [55, 72], [75, 50]],
    away: [[7, 50], [18, 28], [18, 42], [18, 56], [18, 70], [29, 36], [29, 50], [29, 64], [42, 40], [42, 60], [54, 50]]
  }
};

const fieldViewDefaults = {
  full: { formation: "433", ball: [50, 50] },
  "attacking-half": { formation: "corner", ball: [50, 78] },
  "left-corner": { formation: "corner", ball: [7, 92] },
  "right-corner": { formation: "corner", ball: [93, 92] },
  "free-kick-zone": { formation: "corner", ball: [50, 62] }
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

function updateTitleLabel() {
  const formationText = formationSelect.value === "custom"
    ? "Custom"
    : formations[formationSelect.value].label;
  formationLabel.textContent = `${formationText} · ${fieldLabels[currentFieldView]}`;
}

function applyFormation(key) {
  if (key === "custom") {
    updateTitleLabel();
    return;
  }

  const formation = formations[key];
  document.querySelectorAll(".player").forEach(player => {
    const team = player.dataset.team;
    const index = Number(player.dataset.index);
    const point = formation[team][index];
    setPosition(player, point[0], point[1]);
  });

  updateTitleLabel();
}

function applyFieldView(view) {
  currentFieldView = view;
  pitch.className = `pitch view-${view}`;
  const defaults = fieldViewDefaults[view];

  if (view !== "full" && formationSelect.value !== "custom") {
    formationSelect.value = defaults.formation;
    applyFormation(defaults.formation);
  } else {
    updateTitleLabel();
  }

  setPosition(ball, defaults.ball[0], defaults.ball[1]);
  resizeCanvas();
}

function setPosition(element, x, y) {
  element.style.left = `${x}%`;
  element.style.top = `${y}%`;
  element.dataset.x = String(x);
  element.dataset.y = String(y);
}

function getPitchPoint(event) {
  const rect = pitch.getBoundingClientRect();
  return {
    x: Math.max(0, Math.min(100, ((event.clientX - rect.left) / rect.width) * 100)),
    y: Math.max(0, Math.min(100, ((event.clientY - rect.top) / rect.height) * 100)),
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

function hexToRgba(hex, alpha) {
  const clean = hex.replace("#", "");
  const value = parseInt(clean, 16);
  const r = (value >> 16) & 255;
  const g = (value >> 8) & 255;
  const b = value & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function drawShape(shape, preview = false) {
  const from = percentToPixels(shape.from);
  const to = percentToPixels(shape.to);
  const color = shape.color || drawingColor.value;

  ctx.save();
  ctx.lineWidth = preview ? 4 : 5;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.strokeStyle = preview ? hexToRgba(color, 0.72) : color;

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

function applyColors() {
  document.documentElement.style.setProperty("--home", homeColor.value);
  document.documentElement.style.setProperty("--away", awayColor.value);
  document.documentElement.style.setProperty("--drawing", drawingColor.value);
  document.documentElement.style.setProperty("--ball", ballColor.value);
}

function showBall() {
  ball.classList.remove("hidden");
  const defaults = fieldViewDefaults[currentFieldView];
  if (!ball.dataset.x || !ball.dataset.y) {
    setPosition(ball, defaults.ball[0], defaults.ball[1]);
  }
}

function hideBall() {
  ball.classList.add("hidden");
}

function resetBoard() {
  drawings = [];
  fieldViewSelect.value = "full";
  formationSelect.value = "433";
  noteInput.value = "";
  notePreview.textContent = "Add a coaching note below.";
  homeColor.value = "#f7faf8";
  awayColor.value = "#17211b";
  drawingColor.value = "#ffffff";
  ballColor.value = "#ffffff";
  applyColors();
  applyFieldView("full");
  applyFormation("433");
  setPosition(ball, 50, 50);
  ball.classList.add("hidden");
  updateTeamVisibility();
  redraw();
}

function flipBoard() {
  document.querySelectorAll(".player").forEach(player => {
    const x = Number(player.dataset.x);
    const y = Number(player.dataset.y);
    setPosition(player, 100 - x, 100 - y);
  });

  if (!ball.classList.contains("hidden")) {
    const x = Number(ball.dataset.x);
    const y = Number(ball.dataset.y);
    setPosition(ball, 100 - x, 100 - y);
  }

  drawings = drawings.map(shape => ({
    ...shape,
    from: { x: 100 - shape.from.x, y: 100 - shape.from.y },
    to: { x: 100 - shape.to.x, y: 100 - shape.to.y }
  }));

  redraw();
}

function startMove(event, element) {
  if (activeTool !== "move") return;
  activeObject = element;
  element.setPointerCapture(event.pointerId);
}

function moveObject(event) {
  if (!activeObject || activeTool !== "move") return;
  const point = getPitchPoint(event);
  setPosition(activeObject, point.x, point.y);

  if (activeObject.classList.contains("player")) {
    formationSelect.value = "custom";
    updateTitleLabel();
  }
}

function endMove(event) {
  if (!activeObject) return;
  activeObject.releasePointerCapture(event.pointerId);
  activeObject = null;
}

playersLayer.addEventListener("pointerdown", event => {
  const player = event.target.closest(".player");
  if (!player) return;
  startMove(event, player);
});

playersLayer.addEventListener("pointermove", moveObject);
playersLayer.addEventListener("pointerup", endMove);
playersLayer.addEventListener("pointercancel", () => {
  activeObject = null;
});

ball.addEventListener("pointerdown", event => {
  event.stopPropagation();
  startMove(event, ball);
});

ball.addEventListener("pointermove", event => {
  event.stopPropagation();
  moveObject(event);
});

ball.addEventListener("pointerup", event => {
  event.stopPropagation();
  endMove(event);
});

ball.addEventListener("pointercancel", () => {
  activeObject = null;
});

pitch.addEventListener("pointerdown", event => {
  if (activeTool === "move") return;
  drawing = true;
  startPoint = getPitchPoint(event);
});

pitch.addEventListener("pointermove", event => {
  if (!drawing || activeTool === "move") return;
  const current = getPitchPoint(event);
  redraw({ type: activeTool, from: startPoint, to: current, color: drawingColor.value });
});

pitch.addEventListener("pointerup", event => {
  if (!drawing || activeTool === "move") return;
  const endPoint = getPitchPoint(event);
  drawings.push({ type: activeTool, from: startPoint, to: endPoint, color: drawingColor.value });
  drawing = false;
  startPoint = null;
  redraw();
});

pitch.addEventListener("pointercancel", () => {
  drawing = false;
  startPoint = null;
  redraw();
});

toolButtons.forEach(button => {
  button.addEventListener("click", () => updateTool(button.dataset.tool));
});

formationSelect.addEventListener("change", event => applyFormation(event.target.value));
fieldViewSelect.addEventListener("change", event => applyFieldView(event.target.value));

noteInput.addEventListener("input", event => {
  const value = event.target.value.trim();
  notePreview.textContent = value || "Add a coaching note below.";
});

toggleHome.addEventListener("change", updateTeamVisibility);
toggleAway.addEventListener("change", updateTeamVisibility);

[homeColor, awayColor, drawingColor, ballColor].forEach(input => {
  input.addEventListener("input", () => {
    applyColors();
    redraw();
  });
});

showBallBtn.addEventListener("click", showBall);
hideBallBtn.addEventListener("click", hideBall);

clearDrawingsBtn.addEventListener("click", () => {
  drawings = [];
  redraw();
});

flipBoardBtn.addEventListener("click", flipBoard);
resetBtn.addEventListener("click", resetBoard);
exportBtn.addEventListener("click", exportBoardAsPng);

async function exportBoardAsPng() {
  const area = document.getElementById("captureArea");
  const rect = area.getBoundingClientRect();

  const clone = area.cloneNode(true);
  clone.setAttribute("xmlns", "http://www.w3.org/1999/xhtml");

  const svgData = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${rect.width}" height="${rect.height}">
      <foreignObject width="100%" height="100%">
        ${new XMLSerializer().serializeToString(clone)}
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
    link.download = "football-tactic-board.png";
    link.href = exportCanvas.toDataURL("image/png");
    link.click();
  };

  image.src = url;
}


function isFullscreenActive() {
  return document.fullscreenElement === captureArea || captureArea.classList.contains("is-fullscreen");
}

function updateFullscreenButtons() {
  const label = isFullscreenActive() ? "Exit Fullscreen" : "Fullscreen";
  fullscreenBtn.textContent = label;
  boardFullscreenBtn.textContent = label;
}

async function toggleFullscreen() {
  try {
    if (document.fullscreenElement) {
      await document.exitFullscreen();
      captureArea.classList.remove("is-fullscreen");
      document.body.classList.remove("fullscreen-fallback");
    } else if (captureArea.requestFullscreen) {
      await captureArea.requestFullscreen();
    } else {
      captureArea.classList.toggle("is-fullscreen");
      document.body.classList.toggle("fullscreen-fallback", captureArea.classList.contains("is-fullscreen"));
    }
  } catch (error) {
    captureArea.classList.toggle("is-fullscreen");
    document.body.classList.toggle("fullscreen-fallback", captureArea.classList.contains("is-fullscreen"));
  }

  updateFullscreenButtons();
  setTimeout(resizeCanvas, 80);
}

document.addEventListener("fullscreenchange", () => {
  if (!document.fullscreenElement) {
    captureArea.classList.remove("is-fullscreen");
    document.body.classList.remove("fullscreen-fallback");
  }
  updateFullscreenButtons();
  setTimeout(resizeCanvas, 80);
});

document.addEventListener("keydown", event => {
  if (event.key === "Escape" && captureArea.classList.contains("is-fullscreen")) {
    captureArea.classList.remove("is-fullscreen");
    document.body.classList.remove("fullscreen-fallback");
    updateFullscreenButtons();
    setTimeout(resizeCanvas, 80);
  }
});

fullscreenBtn.addEventListener("click", toggleFullscreen);
boardFullscreenBtn.addEventListener("click", toggleFullscreen);

window.addEventListener("resize", resizeCanvas);

createPlayers();
applyColors();
applyFormation("433");
applyFieldView("full");
updateTool("move");
updateTeamVisibility();
setPosition(ball, 50, 50);
resizeCanvas();
