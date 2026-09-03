
import typing
import pdfplumber
from collections import Counter

PDF_PATH = "/Users/nikhilvijayan/Code/timetable-local/Stevenage, Hertford North, Enfield Chase, Welwyn Garden City, Hatfield and Potters Bar to London.pdf"
OPERATOR_TOKENS = {"GN", "TL"}
OPERATOR_X_MIN = 150
STATION_X_MAX = 160
PAGE_RANGES:list[tuple[range, str, str]] = [
  (range(0, 12), "weekday", "to_london"),
  (range(12, 19), "saturday", "to_london"),
  (range(19, 25), "sunday", "to_london"),
  (range(25, 36), "weekday", "from_london"),
  (range(36, 43), "saturday", "from_london"),
  (range(43, 49), "sunday", "from_london"),
]

def find_operator_row(
  words: list[dict[str, str | float]]
) -> tuple[None, dict]:
  op_words = [w for w in words if w["text"] in OPERATOR_TOKENS and w["x0"] > OPERATOR_X_MIN]
  if not op_words:
    return None, {}
  y_counts = Counter(round(w["top"]) for w in op_words)

def extract_page_service(
  page: pdfplumber.page.Page,
  direction: str
) -> None:
  # words = page.extract_words()
  ...


def extract_section(
  pdf: pdfplumber.PDF,
  page_range: range,
  direction: str
) -> list[dict[str, str | None]]:
  seen = {}
  for page_idx in page_range:

def main() -> None:
  result:dict[str, dict[str, list[str]]] = {
    "weekday": {"to_london": [], "from_london": []},
    "saturday": {"to_london": [], "from_london": []},
    "sunday": {"to_london": [], "from_london": []},
  }
 
  try:
    with pdfplumber.open(PDF_PATH) as pdf:
      for page_range, day, direction in PAGE_RANGES:
        print("some stuff here")
      
  except FileNotFoundError:
    print(f"PDF not found {PDF_PATH}")
    return

if __name__ == "__main__":
  main()