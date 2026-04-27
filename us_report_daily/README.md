# USdaily HTML Reporter (No xlwings)

## What it does
- Read market data directly from XLSM using openpyxl (data_only=True)
- Compute T0 / 1D / 1M / YTD
- Merge manual content from content/content.json
- Render HTML using templates/template.html
- Output: output/report_YYYYMMDD.html

## Important note (Excel formulas)
openpyxl does NOT calculate formulas.
Your XLSM must be saved with calculated values cached (INFOMAX results visible in Excel and saved).

## Install
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt