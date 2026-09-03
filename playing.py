import pdfplumber

PDF_PATH = "/Users/nikhilvijayan/Code/timetable-local/Stevenage, Hertford North, Enfield Chase, Welwyn Garden City, Hatfield and Potters Bar to London.pdf"

def process_file(page)-> None:
  print("Something...")
  extracted_words = page.extract_words()
  print(extracted_words)

def main() -> None:
  try:
    with pdfplumber.open(PDF_PATH) as pdf:
      process_file(pdf.pages[0])
      return
  except FileNotFoundError:
    print("File not found")
    return

if __name__ == "__main__":
  main()
