# Customer Data Cleaner

A Python + pandas tool that turns a messy CSV export into clean, deduplicated, analysis-ready data. Rows with problems are flagged for review instead of being silently dropped.

## The problem

Real exports from CRMs, forms, and spreadsheets are full of inconsistencies. This tool fixes them in one command:

| Messy input | Cleaned output |
|---|---|
| `  MARIA `, ` o'brien` | `Maria`, `O'Brien` |
| `  JOHN.SMITH@Yahoo.com ` | `john.smith@yahoo.com` |
| `415.555.1234`, `+1 415 555 1234`, `1-415-555-1234` | `(415) 555-1234` |
| `california`, `Calif.`, `ca` | `CA` |
| `3/7/2025`, `17.03.2025`, `Mar 7, 2025` | `2025-03-07`, `2025-03-17`, `2025-03-07` |
| `$1,234.50`, `USD 99.9`, `free` | `1234.5`, `99.9`, *(flagged)* |
| Same customer entered twice with different email casing | One row |

## What you get

Running it on the included sample file (132 messy rows) produces:

```
Cleaning summary
  Rows in input             132
  Duplicates removed        12
  Clean rows                84
  Rows flagged for review   36
  Invalid emails            13
  Missing/invalid phones    14
  Missing amounts           16
```

- **`cleaned_customers.csv`**: only the rows that passed every check
- **`cleaned_customers.xlsx`**: three sheets
  - **Summary**: the counts above
  - **Clean data**: ready to import anywhere
  - **Needs review**: each problem row with an `issues` column that explains exactly what's wrong (for example, `invalid email; missing amount`)

## Quick start

```bash
pip install -r requirements.txt
python make_sample_data.py              # creates messy_customers.csv (fictional data)
python clean_data.py messy_customers.csv
python -m pytest -q                     # run the tests
```

## Adapting it

Each rule is its own small function (`clean_phone`, `clean_date`, `clean_state`, and so on), so it's easy to add new date formats, more state names, or rules for other columns like ZIP codes, company names, or currencies.

## Tech

Python 3.10+, `pandas`, `openpyxl`, `pytest`
