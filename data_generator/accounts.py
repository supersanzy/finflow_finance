import random
from datetime import datetime, timedelta
from decimal import Decimal

import pandas as pd
from sqlalchemy import text

from db_connection import connect_and_validate_db


# ============================================================
# 1. DATABASE CONNECTION
# ============================================================

engine = connect_and_validate_db()


# ============================================================
# 2. RETRIEVE CUSTOMERS
# ============================================================

query = text("""
    SELECT
        customer_id,
        created_at
    FROM finflow_schema.customers
""")

with engine.connect() as connection:
    customers_df = pd.read_sql(query, connection)


print(f"Customers retrieved: {len(customers_df):,}")


# ============================================================
# 3. ACCOUNT CONFIGURATION
# ============================================================

account_types = [
    "SAVINGS",
    "CURRENT"
]

account_statuses = [
    "ACTIVE",
    "DORMANT",
    "CLOSED"
]


# ============================================================
# 4. ACCOUNT GENERATION FUNCTIONS
# ============================================================

def get_number_of_accounts():
    """
    80% of customers receive one account.
    20% of customers receive two accounts.
    """
    return random.choices(
        population=[1, 2],
        weights=[0.80, 0.20],
        k=1
    )[0]


def get_account_status():
    """
    Generate a realistic account status distribution.
    """
    return random.choices(
        population=account_statuses,
        weights=[0.85, 0.10, 0.05],
        k=1
    )[0]


# ============================================================
# 5. GENERATE UNIQUE ACCOUNT NUMBERS
# ============================================================

generated_account_numbers = set()


def generate_account_number():
    """
    Generate a unique 10-digit account number.
    """

    while True:

        account_number = str(
            random.randint(
                10**9,
                (10**10) - 1
            )
        )

        if account_number not in generated_account_numbers:

            generated_account_numbers.add(
                account_number
            )

            return account_number


# ============================================================
# 6. GENERATE ACCOUNT OPENING DATE
# ============================================================

def generate_opened_at(customer_created_at):
    """
    Generate an account opening date between
    customer.created_at and the current time.

    This guarantees:

        opened_at >= customer.created_at
    """

    customer_created_at = (
        pd.Timestamp(customer_created_at)
        .to_pydatetime()
    )

    current_time = datetime.now()

    time_difference = (
        current_time - customer_created_at
    )

    random_seconds = random.randint(
        0,
        int(time_difference.total_seconds())
    )

    return (
        customer_created_at
        + timedelta(seconds=random_seconds)
    )


# ============================================================
# 7. GENERATE ACCOUNT CLOSING DATE
# ============================================================

def generate_closed_at(account_status, opened_at):
    """
    Generate closed_at only for CLOSED accounts.

    CLOSED:
        closed_at > opened_at

    ACTIVE / DORMANT:
        closed_at = None
    """

    if account_status != "CLOSED":
        return None

    current_time = datetime.now()

    time_difference = (
        current_time - opened_at
    )

    total_seconds = int(
        time_difference.total_seconds()
    )

    if total_seconds <= 0:
        return None

    random_seconds = random.randint(
        1,
        total_seconds
    )

    return (
        opened_at
        + timedelta(seconds=random_seconds)
    )


# ============================================================
# 8. GENERATE ACCOUNT BALANCE
# ============================================================

def generate_balance(account_status):
    """
    CLOSED accounts have a zero balance.

    ACTIVE and DORMANT accounts can have
    balances between NGN 0 and NGN 5,000,000.
    """

    if account_status == "CLOSED":
        return Decimal("0.00")

    balance = random.uniform(
        0,
        5_000_000
    )

    return Decimal(
        str(round(balance, 2))
    )


# ============================================================
# 9. GENERATE ACCOUNTS
# ============================================================

accounts_data = []


for _, customer in customers_df.iterrows():

    customer_id = customer["customer_id"]

    customer_created_at = customer["created_at"]

    number_of_accounts = (
        get_number_of_accounts()
    )

    # Prevent duplicate account types
    # for the same customer.
    selected_account_types = random.sample(
        account_types,
        k=number_of_accounts
    )

    for account_type in selected_account_types:

        account_status = get_account_status()

        opened_at = generate_opened_at(
            customer_created_at
        )

        closed_at = generate_closed_at(
            account_status,
            opened_at
        )

        balance = generate_balance(
            account_status
        )

        account = {
            "customer_id": customer_id,
            "account_number": generate_account_number(),
            "account_type": account_type,
            "currency": "NGN",
            "balance": balance,
            "account_status": account_status,
            "opened_at": opened_at,
            "closed_at": closed_at
        }

        accounts_data.append(account)


# ============================================================
# 10. CREATE ACCOUNTS DATAFRAME
# ============================================================

accounts_df = pd.DataFrame(
    accounts_data
)

print(
    f"Accounts generated: "
    f"{len(accounts_df):,}"
)


# ============================================================
# 11. VALIDATE OPENING DATES
# ============================================================

validation_df = accounts_df.merge(
    customers_df,
    on="customer_id",
    how="left"
)

invalid_open_dates = validation_df[
    validation_df["opened_at"]
    < validation_df["created_at"]
]

print(
    f"Invalid opened_at records: "
    f"{len(invalid_open_dates)}"
)


# ============================================================
# 12. VALIDATE CLOSED ACCOUNTS
# ============================================================

invalid_closed_dates = accounts_df[
    (accounts_df["account_status"] == "CLOSED")
    &
    (
        accounts_df["closed_at"].isna()
        |
        (
            accounts_df["closed_at"]
            <= accounts_df["opened_at"]
        )
    )
]

print(
    f"Invalid closed_at records: "
    f"{len(invalid_closed_dates)}"
)


# ============================================================
# 13. VALIDATE NON-CLOSED ACCOUNTS
# ============================================================

invalid_non_closed = accounts_df[
    (accounts_df["account_status"] != "CLOSED")
    &
    (accounts_df["closed_at"].notna())
]

print(
    f"Invalid non-closed records: "
    f"{len(invalid_non_closed)}"
)


# ============================================================
# 14. VALIDATE ACCOUNT NUMBER UNIQUENESS
# ============================================================

duplicate_account_numbers = accounts_df[
    accounts_df["account_number"].duplicated()
]

print(
    f"Duplicate account numbers: "
    f"{len(duplicate_account_numbers)}"
)


# ============================================================
# 15. VALIDATION GATE
# ============================================================

validation_errors = (
    len(invalid_open_dates)
    + len(invalid_closed_dates)
    + len(invalid_non_closed)
    + len(duplicate_account_numbers)
)


if validation_errors > 0:

    raise ValueError(
        f"Validation failed with "
        f"{validation_errors} invalid records. "
        f"Accounts were NOT inserted."
    )


print("All account validations passed.")


# ============================================================
# 16. CLEAR EXISTING ACCOUNT DATA
# ============================================================

truncate_query = text("""
    TRUNCATE TABLE finflow_schema.accounts
    RESTART IDENTITY
""")

with engine.begin() as connection:

    connection.execute(
        truncate_query
    )


# ============================================================
# 17. INSERT ACCOUNTS
# ============================================================

accounts_df.to_sql(
    name="accounts",
    con=engine,
    schema="finflow_schema",
    if_exists="append",
    index=False,
    method="multi"
)

print(
    f"{len(accounts_df):,} "
    f"accounts inserted successfully."
)


# ============================================================
# 18. VERIFY INSERT
# ============================================================

verify_query = text("""
    SELECT COUNT(*)
    FROM finflow_schema.accounts
""")

with engine.connect() as connection:

    account_count = (
        connection
        .execute(verify_query)
        .scalar()
    )


print(
    f"Accounts in database: "
    f"{account_count:,}"
)