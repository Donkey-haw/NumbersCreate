from numbers_parser import Document
import sys

def main():
    doc = Document("numbers/sheet_name_test.numbers")
    sheet = doc.sheets[0]
    print(f"Read sheet name: '{sheet.name}'")

if __name__ == "__main__":
    main()
