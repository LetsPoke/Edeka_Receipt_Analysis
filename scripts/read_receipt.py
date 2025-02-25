import os
from parsers.receipt_parser import parse_receipt
from utils.file_handler import save_json


def main():
    input_folder = "receipts/pdfs/"
    output_file = "parsed_receipts.json"
    all_data = []

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            parsed = parse_receipt(pdf_path)
            all_data.append(parsed)

    save_json(all_data, output_file)
    print(f"Parsing complete. {len(all_data)} PDFs processed.")


if __name__ == "__main__":
    main()
