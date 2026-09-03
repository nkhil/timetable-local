# Plan: Offline Train Departure Board

## Context
Build an offline train departure board for Harringay (HGY) from a National Rail PDF timetable. Two deliverables: `extract.py` (PDF → JSON) and `index.html` (self-contained departure board). The PDF is already present; `pdfplumber` is not installed.

---

## Step 0 — Install dependency

```bash
pip3 install pdfplumber --break-system-packages
```

---

## Step 1 — `extract.py`

**File**: `/Users/nikhilvijayan/Code/timetable-local/extract.py`

### Constants

```python
PDF_PATH = "/Users/nikhilvijayan/Code/timetable-local/Stevenage, Hertford North, Enfield Chase, Welwyn Garden City, Hatfield and Potters Bar to London.pdf"
OUTPUT_PATH = "/Users/nikhilvijayan/Code/timetable-local/timetable.json"
STATION_CODE = "HGY"
OPERATOR_TOKENS = {"GN", "TL"}
TIME_RE = re.compile(r"^[012]\d[0-5]\d$")
COL_X_TOLERANCE = 18   # px
Y_TOLERANCE = 3        # px
OPERATOR_X_MIN = 150   # operator tokens appear right of this
STATION_X_MAX = 160    # station codes appear left of this

PAGE_RANGES = [
    (range(0, 12),  "weekday",   "to_london"),
    (range(12, 19), "saturday",  "to_london"),
    (range(19, 25), "sunday",    "to_london"),
    (range(25, 36), "weekday",   "from_london"),
    (range(36, 43), "saturday",  "from_london"),
    (range(43, 49), "sunday",    "from_london"),
]

# Most terminal first — first match wins per service
TO_LONDON_DESTS = [
    ("BFR", "Blackfriars"),
    ("KGX", "Kings Cross"),
    ("MOG", "Moorgate"),
    ("FPK", "Finsbury Park"),
]
FROM_LONDON_DESTS = [
    ("SVG", "Stevenage"),
    ("HFN", "Hertford North"),
    ("ENC", "Enfield Chase"),
    ("WLW", "Welwyn North"),
    ("WGC", "Welwyn Garden City"),
]
```

### Functions

**`find_operator_row(words)`**
- Filter words where `text in OPERATOR_TOKENS and x0 > OPERATOR_X_MIN`
- Round each `top` to int; use Counter to find the y with most hits → `op_y`
- Return `(op_y, {round(w['x0'],1): w['text'] for w at op_y})`
- Return `(None, {})` if no operator words found

**`nearest_col(x, col_xs, tol)`**
- Find the closest value in `col_xs` to `x`; return it if within `tol`, else `None`

**`get_times_at_station(words, station_code, col_xs)`**
- Find words where `text == station_code and x0 < STATION_X_MAX`; get their `top` values
- For each such `top`, scan all words within ±`Y_TOLERANCE` matching `TIME_RE`
- Match each time to `nearest_col`; store `result[col_x] = time_str` (first-seen wins)
- Return `result` dict

**`extract_page_services(page, direction)`**
```
words = page.extract_words()
op_y, col_ops = find_operator_row(words)
if not col_ops: return []
col_xs = sorted(col_ops.keys())
hgy_map = get_times_at_station(words, STATION_CODE, col_xs)
if not hgy_map: return []
dest_list = TO_LONDON_DESTS if direction == "to_london" else FROM_LONDON_DESTS
dest_maps = {code: get_times_at_station(words, code, col_xs) for code, _ in dest_list}
services = []
for col_x in sorted(hgy_map.keys()):
    depart = hgy_map[col_x]
    operator = col_ops.get(col_x, "GN")
    dest_name = dest_time = None
    for code, name in dest_list:
        if col_x in dest_maps[code]:
            dest_name, dest_time = name, dest_maps[code][col_x]
            break
    services.append({"depart": depart, "dest_name": dest_name, "dest_time": dest_time, "operator": operator})
return services
```

**`extract_section(pdf, page_range, direction)`**
- Iterate pages in range; collect services; deduplicate by `depart` time (first-seen wins)
- Return sorted by `depart` string (lexicographic = chronological for HHMM)

**`main()`**
- Build result dict; call `extract_section` for each page range; write JSON; print summary counts

---

## Step 2 — `index.html`

**File**: `/Users/nikhilvijayan/Code/timetable-local/index.html`

Single file — all CSS + JS inline. JSON pasted as `const TIMETABLE = {...};` (avoids `fetch()` / file:// issues).

### Layout

```
header: station name, live HH:MM:SS clock, day label
main#board: 2-column grid (collapses to 1 on mobile)
  section: "To London"  → div#panel-to_london
  section: "From London" → div#panel-from_london
footer: note about file:// and python3 -m http.server fallback
```

### JS functions

**`getDayType()`** — `getDay()` → `"weekday"|"saturday"|"sunday"`

**`getNowMinutes()`** — hours×60 + minutes

**`timeToMinutes(hhmm)`** — parse HHMM string to integer minutes

**`minutesUntil(departHHMM, nowMinutes)`**
```javascript
let diff = timeToMinutes(departHHMM) - nowMinutes;
if (diff < -120) diff += 1440;   // midnight wrap: -120 separates "past" from "next day"
return diff;
```

**`getNext5(direction)`**
- Map trains → add `minutesAway`; filter `>= 0`; sort by `minutesAway`; slice first 5

**`renderPanel(direction)`**
- Clear container; for each of next5 render a `.train-row` div with:
  - `depart` formatted as `HH:MM`
  - dest name + arrival time (greyed)
  - operator badge (`.badge-GN` or `.badge-TL`, styled distinctly)
  - countdown: `"NOW"` at 0, `"X min"` otherwise; class `urgent` when `≤ 2`
  - first row gets class `soonest`

**`renderAll()`** — calls `renderPanel` for both directions

**`updateClock()`** — updates `#clock` and `#day-label` every second

**Bootstrap**: `renderAll(); updateClock(); setInterval(updateClock, 1000); setInterval(renderAll, 30_000);`

### Dark theme CSS variables
```css
--bg: #0d1117; --surface: #161b22; --border: #30363d;
--text-primary: #e6edf3; --text-muted: #8b949e;
--urgent: #f85149; --highlight-row: #1c2128;
--gn-badge: #1f4e79; --tl-badge: #2d6a4f;
```

### Midnight wrap rationale
At 23:55 (nowMinutes=1435):
- `0006` train: diff = 6−1435 = −1429 < −120 → +1440 → **11 min** ✓
- `2350` train: diff = 1430−1435 = −5, not < −120 → stays −5 → filtered out ✓

---

## Step 3 — Embed JSON

After `extract.py` runs, paste `timetable.json` contents into `index.html`:
```javascript
const TIMETABLE = { ...json contents... };
```

---

## Verification

1. **Count check**: `python3 -c "import json; d=json.load(open('timetable.json')); [print(f'{k} {dk}: {len(dv)}') for k,v in d.items() for dk,dv in v.items()]"`
   Expected: weekday 89/96, saturday 77/79, sunday 71/75

2. **No null destinations**: `python3 -c "import json; d=json.load(open('timetable.json')); print([s for v in d.values() for dv in v.values() for s in dv if s['dest_name'] is None])"`
   Expected: `[]`

3. **Sort check**: first train is `0006`, last is `2350` in weekday to_london

4. **HTML**: Open in browser; verify clock ticks, day label, 5 trains per panel, countdowns update

5. **Midnight edge**: Temporarily hardcode `getNowMinutes = () => 1438` in browser console; verify `0006` shows as "8 min"
