import re
import json
from collections import Counter

import pdfplumber

PDF_PATH = "/Users/nikhilvijayan/Code/timetable-local/Stevenage, Hertford North, Enfield Chase, Welwyn Garden City, Hatfield and Potters Bar to London.pdf"
OUTPUT_PATH = "/Users/nikhilvijayan/Code/timetable-local/timetable.json"

STATION_CODE = "HGY"
OPERATOR_TOKENS = {"GN", "TL"}
TIME_RE = re.compile(r"^[012]\d[0-5]\d$")
COL_X_TOLERANCE = 18
Y_TOLERANCE = 3
OPERATOR_X_MIN = 150
STATION_X_MAX = 160

PAGE_RANGES = [
    (range(0, 12),  "weekday",   "to_london"),
    (range(12, 19), "saturday",  "to_london"),
    (range(19, 25), "sunday",    "to_london"),
    (range(25, 36), "weekday",   "from_london"),
    (range(36, 43), "saturday",  "from_london"),
    (range(43, 49), "sunday",    "from_london"),
]

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


def find_operator_row(words):
    op_words = [w for w in words if w["text"] in OPERATOR_TOKENS and w["x0"] > OPERATOR_X_MIN]
    if not op_words:
        return None, {}
    y_counts = Counter(round(w["top"]) for w in op_words)
    op_y = y_counts.most_common(1)[0][0]
    col_ops = {
        round(w["x0"], 1): w["text"]
        for w in op_words
        if abs(w["top"] - op_y) < 2
    }
    return op_y, col_ops


def nearest_col(x, col_xs, tol=COL_X_TOLERANCE):
    best = None
    best_dist = tol + 1
    for cx in col_xs:
        d = abs(x - cx)
        if d < best_dist:
            best_dist = d
            best = cx
    return best if best_dist <= tol else None


def get_times_at_station(words, station_code, col_xs):
    station_tops = [
        w["top"]
        for w in words
        if w["text"] == station_code and w["x0"] < STATION_X_MAX
    ]
    result = {}
    for top in station_tops:
        for w in words:
            if abs(w["top"] - top) <= Y_TOLERANCE and TIME_RE.match(w["text"]):
                col = nearest_col(w["x0"], col_xs)
                if col is not None and col not in result:
                    result[col] = w["text"]
    return result


def extract_page_services(page, direction):
    words = page.extract_words()
    op_y, col_ops = find_operator_row(words)
    if not col_ops:
        return []

    col_xs = sorted(col_ops.keys())
    hgy_map = get_times_at_station(words, STATION_CODE, col_xs)
    if not hgy_map:
        return []

    dest_list = TO_LONDON_DESTS if direction == "to_london" else FROM_LONDON_DESTS
    dest_maps = {
        code: get_times_at_station(words, code, col_xs)
        for code, _ in dest_list
    }

    services = []
    for col_x in sorted(hgy_map.keys()):
        depart = hgy_map[col_x]
        operator = col_ops.get(col_x, "GN")
        dest_name = dest_time = None
        for code, name in dest_list:
            if col_x in dest_maps[code]:
                dest_name = name
                dest_time = dest_maps[code][col_x]
                break
        services.append({
            "depart": depart,
            "dest_name": dest_name,
            "dest_time": dest_time,
            "operator": operator,
        })
    return services


def extract_section(pdf, page_range, direction):
    seen = {}
    for page_idx in page_range:
        for svc in extract_page_services(pdf.pages[page_idx], direction):
            if svc["depart"] not in seen:
                seen[svc["depart"]] = svc
    return sorted(seen.values(), key=lambda s: s["depart"])


def main():
    result = {
        "weekday":  {"to_london": [], "from_london": []},
        "saturday": {"to_london": [], "from_london": []},
        "sunday":   {"to_london": [], "from_london": []},
    }

    try:
        with pdfplumber.open(PDF_PATH) as pdf:
            for page_range, day, direction in PAGE_RANGES:
                services = extract_section(pdf, page_range, direction)
                result[day][direction] = services
                print(f"{day:10} {direction:12}: {len(services):3} services", flush=True)
    except FileNotFoundError:
        print(f"PDF not found: {PDF_PATH}")
        print("Install pdfplumber with: pip3 install pdfplumber")
        return

    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nWritten to {OUTPUT_PATH}")

    # Null destination check
    nulls = [
        (day, dr, s)
        for day, v in result.items()
        for dr, svcs in v.items()
        for s in svcs
        if s["dest_name"] is None
    ]
    if nulls:
        print(f"\nWARNING: {len(nulls)} services with no destination:")
        for day, dr, s in nulls:
            print(f"  {day} {dr}: depart={s['depart']} operator={s['operator']}")
    else:
        print("All services have destinations.")


if __name__ == "__main__":
    main()
