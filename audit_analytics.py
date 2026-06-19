"""
Simple Transaction Anomaly Checker
-------------------------------------
A beginner-friendly internal audit tool. It does two things:

  1. Makes up a list of fake company transactions (so we have something to
     test on, since we don't have a real company's data).
  2. Goes through every transaction, one at a time, and checks it against
     a few simple rules that real auditors use to spot problems.

Only basic Python (loops, if-statements, lists, dictionaries) plus pandas
just at the very end to save a nice spreadsheet. Nothing fancy.
"""

import random
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)  # makes sure we get the same "random" data every time we run this

# =========================================================
# STEP 1: Some basic lists to build fake transactions from
# =========================================================
departments = ["Finance", "Marketing", "IT", "Facilities", "Procurement", "Sales"]
employees = ["EMP" + str(i).zfill(3) for i in range(1, 31)]   # EMP001, EMP002, ...
vendors = ["Vendor " + letter for letter in "ABCDEFGHIJKLMNOPQRST"]
categories = ["Office Supplies", "Travel", "Professional Services", "IT Equipment", "Marketing Spend"]

APPROVAL_LIMIT = 10000   # transactions at or above this need extra sign-off
start_date = datetime(2025, 1, 1)

# =========================================================
# STEP 2: Create normal, everyday transactions
# =========================================================
transactions = []

for i in range(500):
    requester = random.choice(employees)
    approver = random.choice(employees)
    while approver == requester:        # in a healthy process, a DIFFERENT person approves
        approver = random.choice(employees)

    transaction = {
        "id": "TXN" + str(i).zfill(4),
        "date": start_date + timedelta(days=random.randint(0, 360)),
        "department": random.choice(departments),
        "requester": requester,
        "approver": approver,
        "vendor": random.choice(vendors),
        "category": random.choice(categories),
        "amount": round(random.uniform(100, 5000), 2),
    }
    transactions.append(transaction)

# =========================================================
# STEP 3: On purpose, plant a few "bad" transactions
# (so later we can check whether our rules actually catch them)
# =========================================================

# a) Self-approved transactions: same person requests AND approves
for i in range(10):
    transactions.append({
        "id": "BAD-SOD-" + str(i).zfill(2),
        "date": start_date + timedelta(days=random.randint(0, 360)),
        "department": random.choice(departments),
        "requester": "EMP005",
        "approver": "EMP005",          # <- same person, this is the red flag
        "vendor": random.choice(vendors),
        "category": random.choice(categories),
        "amount": round(random.uniform(500, 4000), 2),
    })

# b) Duplicate payments: same vendor + same amount, paid again a few days later
for i in range(10):
    amount = round(random.uniform(500, 4000), 2)
    vendor = random.choice(vendors)
    day = random.randint(0, 350)
    for copy_number in range(2):       # create the SAME payment twice
        transactions.append({
            "id": "BAD-DUP-" + str(i).zfill(2) + "-" + str(copy_number),
            "date": start_date + timedelta(days=day + copy_number),
            "department": random.choice(departments),
            "requester": random.choice(employees),
            "approver": random.choice(employees),
            "vendor": vendor,
            "category": random.choice(categories),
            "amount": amount,
        })

# c) Amounts suspiciously close to (but just under) the approval limit
for i in range(10):
    transactions.append({
        "id": "BAD-THRESH-" + str(i).zfill(2),
        "date": start_date + timedelta(days=random.randint(0, 360)),
        "department": "Procurement",
        "requester": "EMP017",
        "approver": random.choice(employees),
        "vendor": random.choice(vendors),
        "category": "Professional Services",
        "amount": round(random.uniform(APPROVAL_LIMIT - 900, APPROVAL_LIMIT - 50), 2),
    })

# d) Suspiciously round amounts (real invoices are almost never this neat)
for i in range(10):
    transactions.append({
        "id": "BAD-ROUND-" + str(i).zfill(2),
        "date": start_date + timedelta(days=random.randint(0, 360)),
        "department": random.choice(departments),
        "requester": random.choice(employees),
        "approver": random.choice(employees),
        "vendor": random.choice(vendors),
        "category": random.choice(categories),
        "amount": random.choice([2500, 3000, 3500, 4000, 4500]),
    })

# e) Amounts way bigger than normal for their category (statistical outliers)
for i in range(10):
    category = random.choice(categories)
    transactions.append({
        "id": "BAD-OUTLIER-" + str(i).zfill(2),
        "date": start_date + timedelta(days=random.randint(0, 360)),
        "department": random.choice(departments),
        "requester": random.choice(employees),
        "approver": random.choice(employees),
        "vendor": random.choice(vendors),
        "category": category,
        "amount": round(random.uniform(15000, 25000), 2),
    })

print("Created", len(transactions), "transactions in total (including planted test cases)")

# =========================================================
# STEP 4: Work out a "normal" average amount per category
# (so later we can spot amounts that are way bigger than usual)
# =========================================================
amounts_by_category = {}
for t in transactions:
    category = t["category"]
    if category not in amounts_by_category:
        amounts_by_category[category] = []
    amounts_by_category[category].append(t["amount"])

average_by_category = {}
for category, amount_list in amounts_by_category.items():
    average_by_category[category] = sum(amount_list) / len(amount_list)

# =========================================================
# STEP 5: Check every transaction, one at a time, against simple rules
# =========================================================
for t in transactions:
    flags = []   # we'll collect plain-English reasons this looks suspicious

    # Rule 1: Same person requested AND approved it (segregation of duties)
    if t["requester"] == t["approver"]:
        flags.append("Self-approved")

    # Rule 2: Amount sits just under the approval limit
    if (APPROVAL_LIMIT - 1000) <= t["amount"] < APPROVAL_LIMIT:
        flags.append("Just under approval limit")

    # Rule 3: Suspiciously round amount (real invoices are rarely this neat)
    if t["amount"] >= 2000 and t["amount"] % 500 == 0:
        flags.append("Round number")

    # Rule 4: Amount is much bigger than normal for its category
    normal_amount = average_by_category[t["category"]]
    if t["amount"] > normal_amount * 4:
        flags.append("Unusually high amount")

    # Rule 5: Processed on a weekend
    if t["date"].weekday() >= 5:   # Monday=0 ... Saturday=5, Sunday=6
        flags.append("Weekend transaction")

    t["flags"] = flags
    t["risk_score"] = len(flags)   # simple scoring: 1 point per rule triggered

# =========================================================
# STEP 6: Check for duplicate payments
# (this one needs to compare every transaction to every OTHER transaction)
# =========================================================
for i in range(len(transactions)):
    for j in range(i + 1, len(transactions)):
        t1 = transactions[i]
        t2 = transactions[j]

        same_vendor = (t1["vendor"] == t2["vendor"])
        same_amount = (t1["amount"] == t2["amount"])
        days_apart = abs((t1["date"] - t2["date"]).days)

        if same_vendor and same_amount and days_apart <= 5:
            t1["flags"].append("Possible duplicate payment")
            t2["flags"].append("Possible duplicate payment")
            t1["risk_score"] += 2     # duplicates count for more, they're a bigger concern
            t2["risk_score"] += 2

# =========================================================
# STEP 7: Turn the risk score into a plain-English risk level
# =========================================================
for t in transactions:
    if t["risk_score"] >= 3:
        t["risk_level"] = "High"
    elif t["risk_score"] == 2:
        t["risk_level"] = "Medium"
    elif t["risk_score"] == 1:
        t["risk_level"] = "Low"
    else:
        t["risk_level"] = "Clear"

    t["flags_text"] = ", ".join(t["flags"]) if t["flags"] else "-"

# =========================================================
# STEP 8: Print a simple summary, like a mini audit memo
# =========================================================
flagged_transactions = [t for t in transactions if t["risk_score"] > 0]
high_risk_transactions = [t for t in transactions if t["risk_level"] == "High"]

print()
print("===================================")
print("       AUDIT SCAN - SUMMARY")
print("===================================")
print("Total transactions checked:", len(transactions))
print("Flagged for review:        ", len(flagged_transactions))
print("High risk transactions:    ", len(high_risk_transactions))
print("-----------------------------------")

# count how many times each rule was triggered, just for the printout
rule_names = ["Self-approved", "Just under approval limit", "Round number",
              "Unusually high amount", "Weekend transaction", "Possible duplicate payment"]
for rule in rule_names:
    count = 0
    for t in transactions:
        if rule in t["flags"]:
            count += 1
    print(f"  {rule:28s} -> {count} flagged")
print("===================================")

# =========================================================
# STEP 9: Check our own work
# Did we actually catch the "bad" transactions we planted earlier?
# =========================================================
planted_bad_ids = [t["id"] for t in transactions if t["id"].startswith("BAD-")]
caught = [t for t in transactions if t["id"] in planted_bad_ids and t["risk_score"] > 0]
print(f"\nValidation: caught {len(caught)} out of {len(planted_bad_ids)} planted test cases "
      f"({round(len(caught) / len(planted_bad_ids) * 100)}%)")

# =========================================================
# STEP 10: Save everything to CSV files (so Excel or the dashboard can read them)
# =========================================================
columns_to_save = ["id", "date", "department", "requester", "approver", "vendor",
                    "category", "amount", "risk_score", "risk_level", "flags_text"]

all_df = pd.DataFrame(transactions)
all_df = all_df[columns_to_save]
all_df.to_csv("all_transactions.csv", index=False)

flagged_df = all_df[all_df["risk_score"] > 0].sort_values("risk_score", ascending=False)
flagged_df.to_csv("flagged_transactions.csv", index=False)

print("\nSaved: all_transactions.csv and flagged_transactions.csv")
