I want to build an offline train departure board as a single HTML file. Here's what I need:

The data source
A PDF train timetable (I'll provide the path). It's a National Rail timetable with a grid layout — each column is a service, each row is a station. The PDF has multiple sections (Monday–Friday, Saturday, Sunday) and two directions (to London, from London), spread across ~49 pages.

Step 1 — Extract the timetable data to JSON
Use Python with pdfplumber. The approach:
For each page, find the Operator row — the first dense cluster of GN/TL words with x-coordinate > 150px. Each word in this row marks a service column; record its x-coordinate and operator.
Find the Notes row (single letters A–F near the Operator row) and map each letter to the nearest column x-coordinate.
For each target station, find the station code word (e.g. HGY), collect all 4-digit time strings matching [012]\d[0-5]\d on the same y-coordinate (within ±3px), and match each time to the nearest column x-coordinate within a tolerance of 18px.
For each service column that has a time at the target station, also look up times at key destination stations using the same column-matching logic. Use the "most terminal" station found as the destination label:
To London: Moorgate (MOG), Kings Cross (KGX)
From London: Stevenage (SVG), Welwyn Garden City (WGC), Hertford North (HFN)
Deduplicate services by departure time — the same service can appear on multiple pages.
Sort each list by departure time.
Target station
Harringay, station code HGY.
Page ranges
Pages
Day type
Direction
1–12
Weekday
To London
13–19
Saturday
To London
20–25
Sunday
To London
26–36
Weekday
From London
37–43
Saturday
From London
44–49
Sunday
From London
Output format
Save as timetable.json:
{
  "weekday": {
    "to_london": [
      { "depart": "0835", "dest_name": "Moorgate", "dest_time": "0853", "operator": "GN" }
    ],
    "from_london": []
  },
  "saturday": { "to_london": [], "from_london": [] },
  "sunday":  { "to_london": [], "from_london": [] }
}


Step 2 — Build the offline HTML departure board
A single self-contained index.html with the JSON embedded as a JS variable (no external dependencies, no network requests).
Functionality
Live clock updating every second
Auto-detect day type (weekday / Saturday / Sunday) from the current date
Show the next 5 trains in each direction, side by side
For each train: departure time, destination, operator badge (GN or TL), and minutes until departure
Highlight the next train; show NOW or X min countdown, turning red when ≤ 2 minutes
Refresh the train list every 30 seconds
Handle midnight wrap-around (a 00:06 service is "next" when it's 23:55)
Work from a local file:// URL — embed the JSON directly in the HTML, or note that fetch() won't work on file:// and offer python3 -m http.server as an alternative
Design
Dark theme, clean layout, readable on mobile.

Note: The station code, page ranges, and destination stations can all be adjusted for a different station — the extraction logic is identical.