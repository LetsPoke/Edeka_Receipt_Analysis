> [!NOTE]  
> Was bored and fiddled around with ChatGPT and my own receipt data.  
> Might improve/continue on this the next time I get bored.

# Edeka Receipt Analysis

A small project that parses PDF supermarket receipts (from Edeka), extracts structured data, and analyzes shopping insights. The solution is written in **Python** and uses [pdfplumber](https://github.com/jsvine/pdfplumber) for text extraction.

## Features

- **PDF Parsing**  
  Extracts text from receipts and converts them into structured JSON.
    - Identifies each item, including quantity, unit price, and total price.
    - Handles special cases like coupons, deposits (Pfand), and weight-based items (kg price).

- **JSON to CSV Conversion**  
  Converts the parsed JSON data into a CSV file for easier handling in Excel, Google Sheets, or further data analysis tools.

- **Data Analysis**  
  Performs aggregations and summaries (daily spend, items purchased, top items, etc.) using [pandas](https://pandas.pydata.org/).

## Repository Structure

```
.
├─ Receipts/
│   └─ (Your PDF files go here, see separate README in this folder)
├─ output/
│   ├─ parsed_receipts.json
│   └─ parsed_receipts.csv
├─ read_receipt.py
├─ convert_receipt.py
├─ analyse_receipt.py
└─ README.md (this file)
```

- **Receipts/**  
  Folder containing the PDF receipts.
- **output/**  
  Folder where the parsed JSON and CSV files are saved.
- **read_receipt.py**  
  The main script that extracts data from PDF files and saves them in a JSON format.
- **convert_receipt.py**  
  Converts the JSON data to CSV.
- **analyse_receipt.py**  
  Demonstrates analyses on the CSV data using pandas.

## Installation

1. **Clone the repo**
   ```
   git clone https://github.com/yourusername/Kassenbon-Analysis.git
   ```
2. **Set up a virtual environment (optional but recommended)**
   ```
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```
3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

## Usage

1. **Place your PDF receipts** in the `Receipts/` folder.
2. **Parse receipts** into JSON:
   ```
   python read_receipt.py
   ```
    - The output file (`parsed_receipts.json`) will be generated in the repository root.
3. **Convert JSON** to CSV:
   ```
   python convert_receipt.py
   ```
    - The resulting CSV (`parsed_receipts.csv`) will be created.
4. **Analyze**:
   ```
   python analyse_receipt.py
   ```
    - Prints various summary statistics and aggregations to the console.

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).  
See the `LICENSE` file for details.