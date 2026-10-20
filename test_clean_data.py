"""Unit tests for the cleaning rules.  Run with:  python -m pytest -q"""

import pandas as pd

import clean_data as cd


def test_names():
    assert cd.clean_name("  MARIA ") == "Maria"
    assert cd.clean_name(" o'brien") == "O'Brien"
    assert cd.clean_name("") is None


def test_phones():
    assert cd.clean_phone("415.555.1234") == "(415) 555-1234"
    assert cd.clean_phone("+1 415 555 1234") == "(415) 555-1234"
    assert cd.clean_phone("1-415-555-1234") == "(415) 555-1234"
    assert cd.clean_phone("N/A") is None


def test_states():
    assert cd.clean_state("Calif.") == "CA"
    assert cd.clean_state("new york") == "NY"
    assert cd.clean_state("wa") == "WA"


def test_dates():
    assert cd.clean_date("3/7/2025") == pd.Timestamp("2025-03-07")
    assert cd.clean_date("2025-03-07") == pd.Timestamp("2025-03-07")
    assert cd.clean_date("17.03.2025") == pd.Timestamp("2025-03-17")
    assert cd.clean_date("Mar 7, 2025") == pd.Timestamp("2025-03-07")
    assert pd.isna(cd.clean_date("not a date"))


def test_amounts():
    assert cd.clean_amount("$1,234.50") == 1234.50
    assert cd.clean_amount("USD 99.9") == 99.9
    assert cd.clean_amount("free") is None


def test_dedupe_and_flags():
    df = pd.DataFrame({
        "Customer ID": ["C1", "C2", "C3"],
        "first name": ["ann", "ann", "bo"],
        "LAST NAME": ["lee", "lee", "wu"],
        "Email ": ["ann@x.com", "  ANN@X.COM ", "bo-at-x.com"],
        "phone": ["4155551234", "4155551234", ""],
        "State": ["ca", "ca", "texas"],
        "signup_date": ["2025-01-02", "2025-01-02", "1/2/2025"],
        "Total Spent": ["$10", "$10", ""],
    })
    clean_rows, review, summary = cd.clean(df)
    assert summary["Duplicates removed"] == 1
    assert len(clean_rows) == 1
    assert clean_rows.iloc[0]["email"] == "ann@x.com"
    assert "invalid email" in review.iloc[0]["issues"]
    assert "missing amount" in review.iloc[0]["issues"]
    assert "missing/invalid phone" in review.iloc[0]["issues"]
    assert summary["Missing/invalid phones"] == 1
