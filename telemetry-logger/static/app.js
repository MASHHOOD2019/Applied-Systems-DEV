/* Telemetry dashboard: polls the API, renders stats, table and a
   simple line chart for the selected sensor. Refreshes every 3s. */

const statsEl = document.getElementById("stats");
const readingsBody = document.getElementById("readingsBody");
const sensorSelect = document.getElementById("sensorSelect");
const chart = document.getElementById("chart");
const ctx = chart.getContext("2d");

async function loadStats() {
  const stats = await (await fetch("/api/stats")).json();
  statsEl.innerHTML = `<div class="card"><b>${stats.total_readings}</b>
      <span>Total readings</span></div>` +
    stats.latest.map(r => `<div class="card"><b>${r.value} ${r.unit}</b>
      <span>${r.sensor_id} (latest)</span></div>`).join("");

  const known = [...sensorSelect.options].map(o => o.value);
  for (const s of stats.sensors) {
    if (!known.includes(s.sensor_id)) {
      const opt = document.createElement("option");
      opt.value = s.sensor_id;
      opt.textContent = s.sensor_id;
      sensorSelect.appendChild(opt);
    }
  }
}

async function loadReadings() {
  const rows = await (await fetch("/api/readings?limit=30")).json();
  readingsBody.innerHTML = rows.map(r =>
    `<tr><td>${r.recorded_at}</td><td>${r.sensor_id}</td>
     <td>${r.value}</td><td>${r.unit}</td></tr>`).join("");
}

function drawChart(points) {
  ctx.clearRect(0, 0, chart.width, chart.height);
  if (points.length < 2) return;
  const values = points.map(p => p.value);
  const min = Math.min(...values), max = Math.max(...values);
  const span = max - min || 1;
  const pad = 20, w = chart.width - pad * 2, h = chart.height - pad * 2;
  ctx.beginPath();
  points.forEach((p, i) => {
    const x = pad + (i / (points.length - 1)) * w;
    const y = pad + h - ((p.value - min) / span) * h;
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  ctx.strokeStyle = "#2563eb";
  ctx.lineWidth = 2;
  ctx.stroke();
}

async function loadChart() {
  const sensor = sensorSelect.value;
  if (!sensor) return;
  const points = await (await fetch(`/api/sensors/${sensor}/history?limit=50`)).json();
  drawChart(points);
}

async function refresh() {
  await loadStats();
  await loadReadings();
  await loadChart();
}

sensorSelect.addEventListener("change", loadChart);
refresh();
setInterval(refresh, 3000);
