/* QA Bug Tracker: full CRUD in the browser, persisted in localStorage,
   with search, filters, stats and JSON/CSV export for test reports. */

const KEY = "qa-bugs";
const form = document.getElementById("bugForm");
const listEl = document.getElementById("bugList");
const statsEl = document.getElementById("stats");

const seed = [
  { id: 1, title: "Login button unresponsive on mobile", module: "Auth",
    severity: "Critical", status: "Open",
    steps: "1. Open login page on a 360px-wide screen\n2. Tap 'Sign in'\nExpected: login proceeds\nActual: nothing happens",
    created: new Date().toISOString() },
  { id: 2, title: "Cart total ignores discount code", module: "Checkout",
    severity: "Major", status: "Open",
    steps: "1. Add item, apply code SAVE10\nExpected: total drops 10%\nActual: total unchanged",
    created: new Date().toISOString() },
  { id: 3, title: "Footer overlaps content on tablet", module: "Layout",
    severity: "Minor", status: "Fixed",
    steps: "1. Open homepage at 768px width\nExpected: footer below content\nActual: footer covers last paragraph",
    created: new Date().toISOString() },
];

function load() {
  const raw = localStorage.getItem(KEY);
  if (!raw) { localStorage.setItem(KEY, JSON.stringify(seed)); return [...seed]; }
  return JSON.parse(raw);
}
function save(bugs) { localStorage.setItem(KEY, JSON.stringify(bugs)); }
function esc(s) { return s.replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])); }

function render() {
  const bugs = load();
  const q = document.getElementById("search").value.toLowerCase();
  const sev = document.getElementById("filterSeverity").value;
  const stat = document.getElementById("filterStatus").value;
  const open = bugs.filter(b => b.status === "Open");
  const fixed = bugs.filter(b => b.status === "Fixed");
  const critical = open.filter(b => b.severity === "Critical").length;
  const rate = bugs.length ? Math.round((fixed.length / bugs.length) * 100) : 0;
  statsEl.innerHTML =
    `<div class="card"><b>${bugs.length}</b><span>Total bugs</span></div>` +
    `<div class="card"><b>${open.length}</b><span>Open</span></div>` +
    `<div class="card"><b>${critical}</b><span>Critical open</span></div>` +
    `<div class="card"><b>${rate}%</b><span>Fix rate</span></div>`;

  const visible = bugs.filter(b =>
    (!q || (b.title + b.module).toLowerCase().includes(q)) &&
    (!sev || b.severity === sev) && (!stat || b.status === stat));
  listEl.innerHTML = visible.length ? visible.map(b => `
    <div class="bug ${b.status === "Fixed" ? "fixed" : ""}">
      <h3>${esc(b.title)}</h3>
      <span class="tag ${b.severity}">${b.severity}</span>
      <span class="tag ${b.status}">${b.status}</span>
      <span>Module: ${esc(b.module)}</span>
      <pre>${esc(b.steps)}</pre>
      <button onclick="toggleStatus(${b.id})">${b.status === "Open" ? "Mark fixed" : "Reopen"}</button>
      <button class="delete" onclick="removeBug(${b.id})">Delete</button>
    </div>`).join("") : "<p>No bugs match the filters.</p>";
}

form.addEventListener("submit", e => {
  e.preventDefault();
  const bugs = load();
  bugs.unshift({
    id: Date.now(), title: document.getElementById("title").value.trim(),
    module: document.getElementById("module").value.trim(),
    severity: document.getElementById("severity").value, status: "Open",
    steps: document.getElementById("steps").value.trim(),
    created: new Date().toISOString(),
  });
  save(bugs);
  form.reset();
  render();
});

window.toggleStatus = id => {
  const bugs = load();
  const bug = bugs.find(b => b.id === id);
  bug.status = bug.status === "Open" ? "Fixed" : "Open";
  save(bugs); render();
};
window.removeBug = id => {
  save(load().filter(b => b.id !== id));
  render();
};

function download(filename, text, type) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = filename;
  a.click();
}
document.getElementById("exportJson").addEventListener("click", () =>
  download("bug-report.json", JSON.stringify(load(), null, 2), "application/json"));
document.getElementById("exportCsv").addEventListener("click", () => {
  const rows = [["id", "title", "module", "severity", "status", "created"],
    ...load().map(b => [b.id, `"${b.title.replace(/"/g, '""')}"`, b.module, b.severity, b.status, b.created])];
  download("bug-report.csv", rows.map(r => r.join(",")).join("\n"), "text/csv");
});

["search", "filterSeverity", "filterStatus"].forEach(id =>
  document.getElementById(id).addEventListener("input", render));
render();
