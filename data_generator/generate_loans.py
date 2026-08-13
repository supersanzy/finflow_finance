import random
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

import pandas as pd
from sqlalchemy import text

from db_connection import connect_and_validate_db


# ============================================================
# CONFIGURATION
# ============================================================

NUM_LOANS = 3000

LOAN_TYPES = [
    "PERSONAL",
    "BUSINESS",
    "AUTO",
    "HOME",
    "EDUCATION"
]

LOAN_STATUS_WEIGHTS = {
    "ACTIVE": 0.65,
    "PAID_OFF": 0.25,
    "DEFAULTED": 0.10
}


# ============================================================
# DATABASE CONNECTION
# ============================================================

engine = connect_and_validate_db()

print("Database connection successful.")


# ============================================================
# RETRIEVE VALID CUSTOMER-ACCOUNT PAIRS
# ============================================================

query = """
SELECT
    a.account_id,
    a.customer_id,
    a.opened_at,
    a.account_status
FROM finflow_schema.accounts a
JOIN finflow_schema.customers c
    ON a.customer_id = c.customer_id
WHERE a.account_status IN ('ACTIVE', 'DORMANT')
"""

accounts_df = pd.read_sql(query, engine)

print(f"Valid customer-account pairs retrieved: {len(accounts_df)}")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def generate_loan_reference(existing_references):
    while True:
        reference = (
            f"LOAN-"
            f"{random.randint(1000000000, 9999999999)}"
        )

        if reference not in existing_references:
            existing_references.add(reference)
            return reference


def generate_principal_amount(loan_type):

    ranges = {
        "PERSONAL": (100_000, 2_000_000),
        "BUSINESS": (500_000, 10_000_000),
        "AUTO": (1_000_000, 15_000_000),
        "HOME": (5_000_000, 50_000_000),
        "EDUCATION": (200_000, 5_000_000)
    }

    minimum, maximum = ranges[loan_type]

    amount = random.randint(
        minimum // 1000,
        maximum // 1000
    ) * 1000

    return Decimal(amount)


def generate_interest_rate(loan_type):

    ranges = {
        "PERSONAL": (15, 30),
        "BUSINESS": (18, 32),
        "AUTO": (12, 25),
        "HOME": (10, 20),
        "EDUCATION": (8, 18)
    }

    minimum, maximum = ranges[loan_type]

    return Decimal(
        str(round(random.uniform(minimum, maximum), 2))
    )


def generate_term_months(loan_type):

    terms = {
        "PERSONAL": [6, 12, 18, 24, 36],
        "BUSINESS": [12, 24, 36, 48, 60],
        "AUTO": [24, 36, 48, 60],
        "HOME": [60, 120, 180, 240],
        "EDUCATION": [12, 24, 36, 48]
    }

    return random.choice(terms[loan_type])


def calculate_total_repayable(
    principal,
    interest_rate,
    term_months
):
    """
    Simplified interest calculation.

    Interest is calculated using:
    Principal × Annual Interest Rate × Loan Term in Years
    """

    years = Decimal(term_months) / Decimal(12)

    interest = (
        principal
        * (interest_rate / Decimal(100))
        * years
    )

    total = principal + interest

    return total.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def generate_loan_dates(account_opened_at, status, term_months):

    today = datetime.now()

    # Ensure loan approval happens after account opening.
    if pd.isna(account_opened_at):
        account_opened_at = today - timedelta(days=365)

    if isinstance(account_opened_at, pd.Timestamp):
        account_opened_at = account_opened_at.to_pydatetime()

    earliest_date = account_opened_at + timedelta(days=30)

    # Avoid generating approval dates in the future.
    latest_date = today - timedelta(days=1)

    # Fallback in case account opening is very recent.
    if earliest_date >= latest_date:
        earliest_date = today - timedelta(days=30)

    date_range = (
        latest_date - earliest_date
    ).days

    approved_at = earliest_date + timedelta(
        days=random.randint(0, max(date_range, 1))
    )

    # Loan can be disbursed on approval date or shortly afterward.
    disbursed_at = approved_at + timedelta(
        days=random.randint(0, 7)
    )

    maturity_date = (
        disbursed_at
        + timedelta(days=term_months * 30)
    ).date()

    return approved_at, disbursed_at, maturity_date


def generate_outstanding_balance(
    total_repayable,
    status,
    disbursed_at,
    maturity_date
):

    today = datetime.now().date()

    if status == "PAID_OFF":
        return Decimal("0.00")

    if status == "DEFAULTED":

        # Defaulted loans retain a significant unpaid balance.
        percentage_remaining = Decimal(
            str(random.uniform(0.30, 0.95))
        )

    else:
        # ACTIVE loans gradually reduce depending on loan age.
        if maturity_date <= today:
            percentage_remaining = Decimal(
                str(random.uniform(0.01, 0.50))
            )
        else:
            percentage_remaining = Decimal(
                str(random.uniform(0.10, 0.90))
            )

    outstanding = (
        total_repayable
        * percentage_remaining
    )

    return outstanding.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


# ============================================================
# GENERATE LOANS
# ============================================================

loans = []

existing_references = set()

for _ in range(NUM_LOANS):

    account = accounts_df.sample(n=1).iloc[0]

    customer_id = int(account["customer_id"])
    account_id = int(account["account_id"])
    account_opened_at = account["opened_at"]

    loan_type = random.choice(LOAN_TYPES)

    loan_status = random.choices(
        population=list(LOAN_STATUS_WEIGHTS.keys()),
        weights=list(LOAN_STATUS_WEIGHTS.values()),
        k=1
    )[0]

    principal_amount = generate_principal_amount(
        loan_type
    )

    interest_rate = generate_interest_rate(
        loan_type
    )

    term_months = generate_term_months(
        loan_type
    )

    total_repayable_amount = calculate_total_repayable(
        principal_amount,
        interest_rate,
        term_months
    )

    approved_at, disbursed_at, maturity_date = (
        generate_loan_dates(
            account_opened_at,
            loan_status,
            term_months
        )
    )

    outstanding_balance = generate_outstanding_balance(
        total_repayable_amount,
        loan_status,
        disbursed_at,
        maturity_date
    )

    loan_reference = generate_loan_reference(
        existing_references
    )

    loans.append({
        "customer_id": customer_id,
        "account_id": account_id,
        "loan_reference": loan_reference,
        "loan_type": loan_type,
        "loan_status": loan_status,
        "principal_amount": principal_amount,
        "interest_rate": interest_rate,
        "total_repayable_amount": total_repayable_amount,
        "outstanding_balance": outstanding_balance,
        "term_months": term_months,
        "approved_at": approved_at,
        "disbursed_at": disbursed_at,
        "maturity_date": maturity_date
    })


loans_df = pd.DataFrame(loans)

print(f"Loans generated: {len(loans_df)}")


# ============================================================
# VALIDATION
# ============================================================

invalid_customer_account_pairs = loans_df.merge(
    accounts_df[
        ["account_id", "customer_id"]
    ],
    on=["account_id", "customer_id"],
    how="left",
    indicator=True
)

invalid_customer_account_pairs = (
    invalid_customer_account_pairs["_merge"] == "left_only"
).sum()


duplicate_references = (
    loans_df["loan_reference"].duplicated().sum()
)


invalid_dates = (
    (
        loans_df["approved_at"]
        > loans_df["disbursed_at"]
    )
    |
    (
        loans_df["disbursed_at"].dt.date
        > loans_df["maturity_date"]
    )
).sum()


invalid_paid_off = (
    (
        loans_df["loan_status"] == "PAID_OFF"
    )
    &
    (
        loans_df["outstanding_balance"] != 0
    )
).sum()


invalid_outstanding_balance = (
    loans_df["outstanding_balance"]
    > loans_df["total_repayable_amount"]
).sum()


print(
    f"Invalid customer-account pairs: "
    f"{invalid_customer_account_pairs}"
)

print(
    f"Duplicate loan references: "
    f"{duplicate_references}"
)

print(
    f"Invalid date relationships: "
    f"{invalid_dates}"
)

print(
    f"Invalid PAID_OFF balances: "
    f"{invalid_paid_off}"
)

print(
    f"Outstanding balances greater than "
    f"total repayable amount: "
    f"{invalid_outstanding_balance}"
)


# ============================================================
# INSERT INTO POSTGRESQL
# ============================================================

insert_query = text("""
INSERT INTO finflow_schema.loans (
    customer_id,
    account_id,
    loan_reference,
    loan_type,
    loan_status,
    principal_amount,
    interest_rate,
    total_repayable_amount,
    outstanding_balance,
    term_months,
    approved_at,
    disbursed_at,
    maturity_date
)
VALUES (
    :customer_id,
    :account_id,
    :loan_reference,
    :loan_type,
    :loan_status,
    :principal_amount,
    :interest_rate,
    :total_repayable_amount,
    :outstanding_balance,
    :term_months,
    :approved_at,
    :disbursed_at,
    :maturity_date
)
""")


with engine.begin() as connection:

    connection.execute(
        insert_query,
        loans_df.to_dict(orient="records")
    )


print("Loans inserted successfully.")

