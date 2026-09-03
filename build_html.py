"""Generate index.html with timetable.json embedded as a JS variable."""
import json

with open("timetable.json") as f:
    timetable_json = json.dumps(json.load(f), separators=(",", ":"))

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Harringay Departures</title>
<style>
:root {{
  --bg: #0d1117;
  --surface: #161b22;
  --border: #30363d;
  --text-primary: #e6edf3;
  --text-muted: #8b949e;
  --urgent: #f85149;
  --soonest-border: #388bfd;
  --soonest-bg: #1c2128;
  --gn-bg: #1f4e79;
  --tl-bg: #2d5a3d;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: var(--bg);
  color: var(--text-primary);
  font-family: ui-monospace, "SF Mono", "Cascadia Code", monospace;
  min-height: 100vh;
}}
header {{
  text-align: center;
  padding: 1.25rem 1rem 1rem;
  border-bottom: 1px solid var(--border);
}}
#clock {{
  font-size: 2.8rem;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.04em;
  font-weight: 300;
}}
#day-label {{
  color: var(--text-muted);
  font-size: 0.8rem;
  margin-top: 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}}
#station-label {{
  color: var(--text-muted);
  font-size: 0.75rem;
  margin-top: 0.2rem;
}}
#board {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  padding: 1rem;
  max-width: 860px;
  margin: 0 auto;
}}
@media (max-width: 580px) {{
  #board {{ grid-template-columns: 1fr; }}
  #clock {{ font-size: 2rem; }}
}}
.panel-title {{
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin-bottom: 0.6rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--border);
}}
.train-row {{
  display: grid;
  grid-template-columns: 3.2rem 1fr auto auto;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.7rem;
  border-radius: 6px;
  margin-bottom: 0.3rem;
  background: var(--surface);
  border: 1px solid var(--border);
  transition: border-color 0.2s;
}}
.train-row.soonest {{
  background: var(--soonest-bg);
  border-color: var(--soonest-border);
}}
.depart {{
  font-size: 1.1rem;
  font-variant-numeric: tabular-nums;
  font-weight: 600;
}}
.dest-block {{
  overflow: hidden;
}}
.dest-name {{
  font-size: 0.85rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.dest-arr {{
  font-size: 0.7rem;
  color: var(--text-muted);
}}
.badge {{
  font-size: 0.6rem;
  font-weight: 700;
  padding: 2px 5px;
  border-radius: 3px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  flex-shrink: 0;
}}
.badge-GN {{ background: var(--gn-bg); color: #a8d8ff; }}
.badge-TL {{ background: var(--tl-bg); color: #a8f0c0; }}
.countdown {{
  font-size: 0.8rem;
  font-variant-numeric: tabular-nums;
  text-align: right;
  color: var(--text-muted);
  min-width: 3.2rem;
  white-space: nowrap;
}}
.countdown.urgent {{
  color: var(--urgent);
  font-weight: 700;
}}
.no-trains {{
  color: var(--text-muted);
  font-size: 0.85rem;
  padding: 0.75rem 0;
  text-align: center;
}}
footer {{
  text-align: center;
  padding: 1.5rem 1rem;
  color: var(--text-muted);
  font-size: 0.7rem;
  border-top: 1px solid var(--border);
  margin-top: 1rem;
}}
footer code {{
  background: var(--surface);
  padding: 1px 5px;
  border-radius: 3px;
  border: 1px solid var(--border);
}}
</style>
</head>
<body>
<header>
  <div id="clock">--:--:--</div>
  <div id="day-label"></div>
  <div id="station-label">Harringay (HGY)</div>
</header>
<main id="board">
  <section>
    <div class="panel-title">To London</div>
    <div id="panel-to_london"></div>
  </section>
  <section>
    <div class="panel-title">From London</div>
    <div id="panel-from_london"></div>
  </section>
</main>
<footer>
  Works offline &mdash; JSON is embedded directly in this file.<br>
  If trains don&rsquo;t appear on <code>file://</code>, serve locally:
  <code>python3 -m http.server 8080</code> then open <code>http://localhost:8080</code>
</footer>
<script>
const TIMETABLE = {timetable_json};

function getDayType() {{
  const d = new Date().getDay();
  if (d === 0) return "sunday";
  if (d === 6) return "saturday";
  return "weekday";
}}

function getNowMinutes() {{
  const n = new Date();
  return n.getHours() * 60 + n.getMinutes();
}}

function timeToMinutes(hhmm) {{
  return parseInt(hhmm.slice(0, 2), 10) * 60 + parseInt(hhmm.slice(2), 10);
}}

function minutesUntil(departHHMM, nowMinutes) {{
  let diff = timeToMinutes(departHHMM) - nowMinutes;
  if (diff < -120) diff += 1440;
  return diff;
}}

function formatTime(hhmm) {{
  return hhmm.slice(0, 2) + ":" + hhmm.slice(2);
}}

function formatCountdown(mins) {{
  if (mins === 0) return "NOW";
  return mins + " min";
}}

function getNext5(direction) {{
  const dayType = getDayType();
  const trains = TIMETABLE[dayType][direction];
  const now = getNowMinutes();
  return trains
    .map(t => ({{ ...t, minutesAway: minutesUntil(t.depart, now) }}))
    .filter(t => t.minutesAway >= 0)
    .sort((a, b) => a.minutesAway - b.minutesAway)
    .slice(0, 5);
}}

function renderPanel(direction) {{
  const next5 = getNext5(direction);
  const container = document.getElementById("panel-" + direction);
  container.innerHTML = "";

  if (next5.length === 0) {{
    container.innerHTML = '<div class="no-trains">No more trains today</div>';
    return;
  }}

  next5.forEach((t, idx) => {{
    const row = document.createElement("div");
    row.className = "train-row" + (idx === 0 ? " soonest" : "");

    const urgent = t.minutesAway <= 2;
    const destArr = t.dest_time
      ? `<div class="dest-arr">arr ${{formatTime(t.dest_time)}}</div>`
      : "";

    row.innerHTML =
      `<span class="depart">${{formatTime(t.depart)}}</span>` +
      `<span class="dest-block">` +
        `<div class="dest-name">${{t.dest_name ?? "Unknown"}}</div>` +
        destArr +
      `</span>` +
      `<span class="badge badge-${{t.operator}}">${{t.operator}}</span>` +
      `<span class="countdown${{urgent ? " urgent" : ""}}">${{formatCountdown(t.minutesAway)}}</span>`;

    container.appendChild(row);
  }});
}}

function renderAll() {{
  renderPanel("to_london");
  renderPanel("from_london");
}}

function updateClock() {{
  const now = new Date();
  const hh = String(now.getHours()).padStart(2, "0");
  const mm = String(now.getMinutes()).padStart(2, "0");
  const ss = String(now.getSeconds()).padStart(2, "0");
  document.getElementById("clock").textContent = hh + ":" + mm + ":" + ss;

  const dayType = getDayType();
  const dayNames = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
  const label = dayNames[now.getDay()] + " — " +
    dayType.charAt(0).toUpperCase() + dayType.slice(1) + " timetable";
  document.getElementById("day-label").textContent = label;
}}

renderAll();
updateClock();
setInterval(updateClock, 1000);
setInterval(renderAll, 30_000);
</script>
</body>
</html>"""

with open("index.html", "w") as f:
    f.write(html)

print("Written index.html")
print(f"File size: {len(html) / 1024:.1f} KB")
