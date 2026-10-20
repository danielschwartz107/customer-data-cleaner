"""Generate a realistically messy customer export for demoing clean_data.py.

All people here are fictional. Run:  python make_sample_data.py
"""

import csv
import random

random.seed(42)

FIRST = ["john", "MARIA", " priya", "James ", "li", "Ahmed", "sofia", "noah", "Emma", "carlos"]
LAST = ["smith", "GARCIA", "patel ", " o'brien", "chen", "khan", "rossi", "kim", "Johnson", "lopez"]
STATES = ["CA", "california", "Calif.", "NY", "new york", "TX", "texas", "wa", "Washington"]
DATE_FORMATS = ["{m}/{d}/{y}", "{y}-{m:02d}-{d:02d}", "{d:02d}.{m:02d}.{y}", "{mon} {d}, {y}"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def messy_phone() -> str:
    a, b, c = random.randint(200, 999), random.randint(200, 999), random.randint(1000, 9999)
    return random.choices(
        [f"({a}) {b}-{c}", f"{a}-{b}-{c}", f"{a}.{b}.{c}", f"{a}{b}{c}",
         f"+1 {a} {b} {c}", f"1-{a}-{b}-{c}", "N/A", ""],
        weights=[3, 3, 3, 3, 3, 3, 1, 1],
    )[0]


def messy_date() -> str:
    y, m, d = random.choice([2024, 2025, 2026]), random.randint(1, 12), random.randint(1, 28)
    fmt = random.choice(DATE_FORMATS)
    if "{d:02d}.{m:02d}" in fmt:  # European style needs day > 12 to be unambiguous
        d = random.randint(13, 28)
    return fmt.format(y=y, m=m, d=d, mon=MONTHS[m - 1])


def messy_amount() -> str:
    v = round(random.uniform(15, 2500), 2)
    return random.choices(
        [f"${v:,.2f}", f"{v}", f"USD {v}", f" {v:,.2f} ", "", "free"],
        weights=[5, 5, 3, 3, 1, 1],
    )[0]


def main() -> None:
    rows = []
    for i in range(1, 121):
        first, last = random.choice(FIRST), random.choice(LAST)
        email_user = f"{first.strip().lower()}.{last.strip().lower().replace(chr(39), '')}{i}"
        email = random.choices(
            [f"{email_user}@gmail.com", f"  {email_user.upper()}@Yahoo.com ",
             f"{email_user}@outlook.com", f"{email_user}gmail.com"],  # last: missing @
            weights=[4, 3, 3, 1],
        )[0]
        rows.append({
            "Customer ID": f"C{i:04d}",
            "first name": first,
            "LAST NAME": last,
            "Email ": email,
            "phone": messy_phone(),
            "State": random.choice(STATES),
            "signup_date": messy_date(),
            "Total Spent": messy_amount(),
        })

    # Inject exact and near-duplicate rows (same email, different casing/spaces)
    for src in random.sample(rows, 12):
        dup = dict(src)
        dup["Email "] = f"  {src['Email '].strip().upper()} "
        rows.append(dup)
    random.shuffle(rows)

    with open("messy_customers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote messy_customers.csv with {len(rows)} rows")


if __name__ == "__main__":
    main()
