from numbers_parser import Document
import sys

def main():
    doc = Document()
    sheet = doc.sheets[0]
    try:
        sheet.name = "My New Sheet Name"
        doc.save("numbers/sheet_name_test.numbers")
        print("Set sheet name correctly.")
    except Exception as e:
        print("Error setting name:", e)

if __name__ == "__main__":
    main()
