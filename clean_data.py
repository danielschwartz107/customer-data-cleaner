"""
Customer Data Cleaner
---------------------
Turns a messy CSV export into a clean, deduplicated dataset and flags rows that
need a human to look at them.

Usage:
    python clean_data.py messy_customers.csv
    python clean_data.py input.csv --out cleaned_customers
"""

import argparse
import re

import pandas as pd

STATE_MAP = {
    "ca": "CA", "california": "CA", "calif": "CA",
    "ny": "NY", "new york": "NY",
    "tx": "TX", "texas": "TX",
    "wa": "WA", "washington": "WA",
}
EMAIL_RE = re.compile(r"^[\w.+'-]+@[\w-]+(\.[\w-]+)+$")
DATE_FORMATS = ["%m/%d/%Y", "%Y-%m-%d", "%d.%m.%Y", "%b %d, %Y"]


def snake_case(col: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", col.strip().lower()).strip("_")


def clean_name(value) -> str | None:
    if pd.isna(value) or not str(value).strip():
        return None
    # Title-case each part, preserving apostrophes like O'Brien
    return " ".join(
        "'".join(p.capitalize() for p in word.split("'"))
        for word in str(value).split()
    )


def clean_email(value) -> str | None:
    if pd.isna(value):
        return None
    email = str(value).strip().lower()
    return email or None


def clean_phone(value) -> str | None:
    digits = re.sub(r"\D", "", str(value)) if pd.notna(value) else ""
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        return None
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"


def clean_state(value) -> str | None:
    if pd.isna(value):
        return None
    key = str(value).strip().lower().rstrip(".")
    return STATE_MAP.get(key, str(value).strip().upper() or None)


def clean_date(value):
    if pd.isna(value) or not str(value).strip():
        return pd.NaT
    text = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return pd.to_datetime(text, format=fmt)
        except ValueError:
            continue
    return pd.NaT


def clean_amount(value) -> float | None:
    if pd.isna(value):
        return None
    text = re.sub(r"[^\d.]", "", str(value))
    try:
        return round(float(text), 2) if text else None
    except ValueError:
        return None


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Return (cleaned rows, rows needing review, summary stats)."""
    raw_count = len(df)
    df = df.rename(columns=snake_case)

    df["first_name"] = df["first_name"].map(clean_name)
    df["last_name"] = df["last_name"].map(clean_name)
    df["email"] = df["email"].map(clean_email)
    df["phone"] = df["phone"].map(clean_phone)
    df["state"] = df["state"].map(clean_state)
    df["signup_date"] = df["signup_date"].map(clean_date)
    df["total_spent"] = df["total_spent"].map(clean_amount)

    before_dedupe = len(df)
    df = df.drop_duplicates(subset=["email"], keep="first")
    duplicates_removed = before_dedupe - len(df)

    # Flag problems instead of silently dropping data
    issues = []
    for idx, row in df.iterrows():
        problems = []
        if pd.isna(row["email"]) or not EMAIL_RE.match(row["email"]):
            problems.append("invalid email")
        if pd.isna(row["phone"]):
            problems.append("missing/invalid phone")
        if pd.isna(row["signup_date"]):
            problems.append("unparseable date")
        if pd.isna(row["total_spent"]):
            problems.append("missing amount")
        issues.append("; ".join(problems))
    df["issues"] = issues

    review = df[df["issues"] != ""].copy()
    clean_rows = df[df["issues"] == ""].drop(columns="issues").copy()

    for frame in (clean_rows, review):
        frame["signup_date"] = pd.to_datetime(frame["signup_date"]).dt.strftime("%Y-%m-%d")

    summary = {
        "Rows in input": raw_count,
        "Duplicates removed": duplicates_removed,
        "Clean rows": len(clean_rows),
        "Rows flagged for review": len(review),
        "Invalid emails": int(review["issues"].str.contains("invalid email").sum()),
        "Missing/invalid phones": int(review["issues"].str.contains("phone").sum()),
        "Missing amounts": int(review["issues"].str.contains("amount").sum()),
    }
    return clean_rows, review, summary


def export(clean_rows: pd.DataFrame, review: pd.DataFrame, summary: dict, out_base: str) -> None:
    clean_rows.to_csv(f"{out_base}.csv", index=False)
    summary_df = pd.DataFrame(list(summary.items()), columns=["Metric", "Count"])

    with pd.ExcelWriter(f"{out_base}.xlsx", engine="openpyxl") as xl:
        summary_df.to_excel(xl, sheet_name="Summary", index=False)
        clean_rows.to_excel(xl, sheet_name="Clean data", index=False)
        review.to_excel(xl, sheet_name="Needs review", index=False)
        for sheet in xl.sheets.values():
            for col in sheet.columns:
                width = max(len(str(c.value or "")) for c in col) + 2
                sheet.column_dimensions[col[0].column_letter].width = min(width, 50)
            sheet.freeze_panes = "A2"


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean and deduplicate a messy customer CSV")
    parser.add_argument("input", help="Path to the messy CSV")
    parser.add_argument("--out", default="cleaned_customers", help="Output path without extension")
    args = parser.parse_args()

    df = pd.read_csv(args.input, dtype=str)
    clean_rows, review, summary = clean(df)
    export(clean_rows, review, summary, args.out)

    print("Cleaning summary")
    for k, v in summary.items():
        print(f"  {k:<26}{v}")
    print(f"Saved {args.out}.csv and {args.out}.xlsx")


if __name__ == "__main__":
    main()
