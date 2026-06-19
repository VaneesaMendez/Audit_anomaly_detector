# Transaction Anomaly Checker & Risk Dashboard (Beginner-Friendly Version)

A small audit analytics project, written using only basic Python (loops,
if-statements, lists, dictionaries) plus pandas and Streamlit.

## What it does

**`audit_analytics.py`** makes up a list of 560 fake company transactions, then checks every
single one against six simple rules auditors actually use:

- **Self-approved** — the same person both requested and approved the payment
- **Just under approval limit** — amount sits just below the £10,000 sign-off threshold (a classic way to dodge extra scrutiny)
- **Round number** — suspiciously neat amounts that real invoices rarely produce
- **Unusually high amount** — far bigger than the normal spend for that category
- **Weekend transaction** — processed outside normal business days
- **Possible duplicate payment** — same vendor, same amount, paid again within days

Every transaction gets a score based on how many rules it triggers, then a plain-English risk level: Clear, Low, Medium, or High.

To prove the rules actually work, the script deliberately plants 60 "known bad" transactions into the fake data first, then checks whether its own rules catch them. Current result: **100% caught**.

**`dashboard.py`** is a Streamlit dashboard (the same tool used in the
fashion recommender project) that reads the results and displays them as a simple web page: summary numbers, a few charts, and a filterable table.
No HTML, CSS, or JavaScript involved, it's all plain Python.

## How to run it

```bash
pip install pandas streamlit

python audit_analytics.py        # creates the fake data and checks it
streamlit run dashboard.py       # opens the dashboard in your browser
```

Run `audit_analytics.py` first, it creates `all_transactions.csv` and
`flagged_transactions.csv`, which the dashboard then reads.

## Why it's built this way

Every check is a plain `if` statement looping over the data one transaction at a time, nothing vectorised or clever, so each rule reads almost like a sentence ("if the requester and approver are the same person, flag it").

## Notes on the data

All transactions are made up by the script for practice purposes. No real
company or personal data is used anywhere in this project.
