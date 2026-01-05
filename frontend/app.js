const API = "http://127.0.0.1:5000";

const $ = (id) => document.getElementById(id);

let lastState = null;

function status(msg, isErr = false) {
  const el = $("status");
  if (!el) return;
  el.textContent = msg;
  el.classList.toggle("err", isErr);
}

async function api(path, method = "GET", body = null) {
  const res = await fetch(`${API}${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} - ${await res.text()}`);
  return await res.json();
}

function renderJSON(data) {
  const el = $("state");
  if (el) el.textContent = JSON.stringify(data, null, 2);
}

function clamp(v, a, b) {
  return Math.max(a, Math.min(b, v));
}

function makeFieldEvaluator(exprX, exprY) {
  // Very small expression evaluator for x,y with Math support.
  // Supports: x, y, numbers, + - * / ( ) and Math.* like sin, cos, sqrt, abs, pow
  // Example: "y", "-x", "sin(y)", "x/2", "0"
  const safe = (s) =>
    s
      .replaceAll("^", "**") // allow ^ as power if user tries
      .replace(/\bpi\b/gi, "Math.PI")
      .replace(/\be\b/gi, "Math.E")
      .replace(/\bsin\b/gi, "Math.sin")
      .replace(/\bcos\b/gi, "Math.cos")
      .replace(/\btan\b/gi, "Math.tan")
      .replace(/\basin\b/gi, "Math.asin")
      .replace(/\bacos\b/gi, "Math.acos")
      .replace(/\batan\b/gi, "Math.atan")
      .replace(/\bsqrt\b/gi, "Math.sqrt")
      .replace(/\babs\b/gi, "Math.abs")
      .replace(/\bpow\b/gi, "Math.pow")
      .replace(/\bmin\b/gi, "Math.min")
      .replace(/\bmax\b/gi, "Math.max");

  const ex = safe(exprX || "0");
  const ey = safe(exprY || "0");

  let fx, fy;
  try {
    fx = new Function("x", "y", `"use strict"; return (${ex});`);
    fy = new Function("x", "y", `"use strict"; return (${ey});`);
  } catch {
    // fallback if expression is invalid
    fx = () => 0;
    fy = () => 0;
  }

  return (x, y) => {
    let vx = 0, vy = 0;
    try { vx = Number(fx(x, y)); } catch { vx = 0; }
    try { vy = Number(fy(x, y)); } catch { vy = 0; }
    if (!Number.isFinite(vx)) vx = 0;
    if (!Number.isFinite(vy)) vy = 0;
    return { vx, vy };
  };
}

function draw(state) {
  const canvas = $("viz");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const W = canvas.width;
  const H = canvas.height;

  ctx.clearRect(0, 0, W, H);

  const b = state.bounds || { xmin: -10, xmax: 10, ymin: -10, ymax: 10 };
  const xmin = b.xmin, xmax = b.xmax, ymin = b.ymin, ymax = b.ymax;

  // world -> canvas
  const pad = 30;
  const sx = (x) => pad + ((x - xmin) / (xmax - xmin)) * (W - 2 * pad);
  const sy = (y) => H - pad - ((y - ymin) / (ymax - ymin)) * (H - 2 * pad);

  // background box
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, W, H);

  // border
  ctx.strokeStyle = "#cfd6ff";
  ctx.lineWidth = 2;
  ctx.strokeRect(pad, pad, W - 2 * pad, H - 2 * pad);

  // axes
  ctx.strokeStyle = "#e4e7ff";
  ctx.lineWidth = 1;
  ctx.beginPath();
  // y=0 axis
  if (ymin < 0 && ymax > 0) {
    ctx.moveTo(pad, sy(0));
    ctx.lineTo(W - pad, sy(0));
  }
  // x=0 axis
  if (xmin < 0 && xmax > 0) {
    ctx.moveTo(sx(0), pad);
    ctx.lineTo(sx(0), H - pad);
  }
  ctx.stroke();

  // field sampling
  const field = state.field || { x: "0", y: "0" };
  const evalField = makeFieldEvaluator(field.x, field.y);

  // grid resolution
  const cols = 18;
  const rows = 12;

  // compute max magnitude to normalize arrow length
  let maxMag = 1e-6;
  const samples = [];
  for (let i = 0; i <= cols; i++) {
    for (let j = 0; j <= rows; j++) {
      const x = xmin + (i / cols) * (xmax - xmin);
      const y = ymin + (j / rows) * (ymax - ymin);
      const { vx, vy } = evalField(x, y);
      const mag = Math.hypot(vx, vy);
      maxMag = Math.max(maxMag, mag);
      samples.push({ x, y, vx, vy, mag });
    }
  }

  // draw arrows
  ctx.strokeStyle = "#6a77ff";
  ctx.lineWidth = 1;

  const baseLen = 16; // pixels
  for (const s of samples) {
    const nx = s.vx / maxMag;
    const ny = s.vy / maxMag;

    // skip near-zero vectors
    if (Math.abs(nx) + Math.abs(ny) < 0.02) continue;

    const x0 = sx(s.x);
    const y0 = sy(s.y);

    const x1 = x0 + nx * baseLen;
    const y1 = y0 - ny * baseLen; // canvas y is inverted

    // line
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.stroke();

    // arrow head
    const ang = Math.atan2(y1 - y0, x1 - x0);
    const head = 5;
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x1 - head * Math.cos(ang - Math.PI / 6), y1 - head * Math.sin(ang - Math.PI / 6));
    ctx.lineTo(x1 - head * Math.cos(ang + Math.PI / 6), y1 - head * Math.sin(ang + Math.PI / 6));
    ctx.closePath();
    ctx.fillStyle = "#6a77ff";
    ctx.fill();
  }

  // draw particles
  const particles = state.particles || [];
  for (const p of particles) {
    const px = sx(p.x);
    const py = sy(p.y);

    const charge = (p.charge ?? p.q ?? 1); // support either field name
    ctx.beginPath();
    ctx.arc(px, py, 6, 0, Math.PI * 2);
    ctx.fillStyle = charge >= 0 ? "#ff4d4d" : "#2b6cff";
    ctx.fill();
    ctx.strokeStyle = "#111";
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  // label
  ctx.fillStyle = "#111";
  ctx.font = "12px system-ui";
  ctx.fillText(`field: x=${field.x}, y=${field.y} | paused=${state.paused}`, pad, 18);
}

async function refresh() {
  try {
    status("Loading…");
    const data = await api("/api/state");
    lastState = data;
    renderJSON(data);
    draw(data);
    status("OK");
  } catch (e) {
    status(e.message, true);
  }
}

function wireButtons() {
  $("setField")?.addEventListener("click", async () => {
    try {
      status("Setting field…");
      const data = await api("/api/field", "POST", { x: $("fieldX").value, y: $("fieldY").value });
      lastState = data;
      renderJSON(data);
      draw(data);
      status("Field set");
    } catch (e) {
      status(e.message, true);
    }
  });

  $("addParticle")?.addEventListener("click", async () => {
    try {
      status("Adding particle…");
      const data = await api("/api/particle", "POST", {
        x: Number($("px").value),
        y: Number($("py").value),
        charge: Number($("charge").value),
      });
      lastState = data;
      renderJSON(data);
      draw(data);
      status("Particle added");
    } catch (e) {
      status(e.message, true);
    }
  });

  $("step")?.addEventListener("click", async () => {
    try {
      const n = Math.max(1, Number($("n").value || 1));
      status(`Stepping ${n}…`);
      const data = await api("/api/step", "POST", { n });
      lastState = data;
      renderJSON(data);
      draw(data);
      status("Stepped");
    } catch (e) {
      status(e.message, true);
    }
  });

  $("play")?.addEventListener("click", async () => {
    try {
      status("Play…");
      const d = await api("/api/play", "POST");
      lastState = d;
      renderJSON(d);
      draw(d);
      status("Playing");
    } catch (e) {
      status(e.message, true);
    }
  });

  $("pause")?.addEventListener("click", async () => {
    try {
      status("Pause…");
      const d = await api("/api/pause", "POST");
      lastState = d;
      renderJSON(d);
      draw(d);
      status("Paused");
    } catch (e) {
      status(e.message, true);
    }
  });

  $("reset")?.addEventListener("click", async () => {
    try {
      status("Reset…");
      const d = await api("/api/reset", "POST");
      lastState = d;
      renderJSON(d);
      draw(d);
      status("Reset done");
    } catch (e) {
      status(e.message, true);
    }
  });

  $("refresh")?.addEventListener("click", refresh);
}

// Optional: simple animation loop by calling /api/step repeatedly when not paused
let ticking = false;
async function tickLoop() {
  if (ticking) return;
  ticking = true;
  try {
    while (true) {
      await new Promise((r) => setTimeout(r, 120));
      if (!lastState) continue;
      if (lastState.paused) continue;

      const data = await api("/api/step", "POST", { n: 1 });
      lastState = data;
      renderJSON(data);
      draw(data);
    }
  } catch (e) {
    status(e.message, true);
  }
}

wireButtons();
refresh();
tickLoop();
