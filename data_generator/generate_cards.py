import random
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import text

from db_connection import connect_and_validate_db


engine = connect_and_validate_db()


# ============================================================
# CONFIGURATION
# ============================================================

CARD_TYPES = ["DEBIT", "CREDIT"]
CARD_STATUSES = ["ACTIVE", "INACTIVE"]

CARD_TYPE_WEIGHTS = [75, 25]
CARD_STATUS_WEIGHTS = [85, 15]

CARD_COVERAGE = 0.70


# ============================================================
# RETRIEVE ELIGIBLE ACCOUNTS
# ============================================================

with engine.connect() as connection:

    eligible_accounts_query = text("""
        SELECT
            account_id,
            customer_id,
            opened_at,
            closed_at
        FROM finflow_schema.accounts
        WHERE closed_at IS NULL
    """)

    accounts_df = pd.read_sql(
        eligible_accounts_query,
        connection
    )


print(f"Eligible accounts retrieved: {len(accounts_df)}")


# ============================================================
# SELECT ACCOUNTS THAT WILL RECEIVE CARDS
# ============================================================

number_of_cards = int(
    len(accounts_df) * CARD_COVERAGE
)

selected_accounts = accounts_df.sample(
    n=number_of_cards,
    random_state=42
).reset_index(drop=True)


print(f"Accounts selected for cards: {len(selected_accounts)}")


# ============================================================
# GENERATE UNIQUE CARD NUMBERS
# ============================================================

used_card_numbers = set()


def generate_card_number():

    while True:

        card_number = "".join(
            str(random.randint(0, 9))
            for _ in range(16)
        )

        if card_number not in used_card_numbers:

            used_card_numbers.add(card_number)

            return card_number


# ============================================================
# GENERATE CARDS
# ============================================================

print("Generating cards...")

cards = []

current_time = datetime.now()

for _, account in selected_accounts.iterrows():

    account_id = int(account["account_id"])
    customer_id = int(account["customer_id"])

    opened_at = pd.to_datetime(
        account["opened_at"]
    ).to_pydatetime()

    # Card must be issued on or after the account was opened.
    issued_start = opened_at
    issued_end = current_time

    if issued_start > issued_end:
        issued_at = issued_end
    else:
        issued_at = issued_start + timedelta(
            seconds=random.randint(
                0,
                int(
                    (issued_end - issued_start).total_seconds()
                )
            )
        )

    # Card expires between 3 and 5 years after issuance.
    expiration_years = random.randint(3, 5)

    expires_at = (
        issued_at
        + timedelta(days=365 * expiration_years)
    ).date()

    card_type = random.choices(
        CARD_TYPES,
        weights=CARD_TYPE_WEIGHTS,
        k=1
    )[0]

    card_status = random.choices(
        CARD_STATUSES,
        weights=CARD_STATUS_WEIGHTS,
        k=1
    )[0]

    cards.append(
        {
            "customer_id": customer_id,
            "account_id": account_id,
            "card_number": generate_card_number(),
            "card_type": card_type,
            "card_status": card_status,
            "issued_at": issued_at,
            "expires_at": expires_at
        }
    )


cards_df = pd.DataFrame(cards)

print(f"Cards generated: {len(cards_df)}")


# ============================================================
# INSERT CARDS
# ============================================================

print("Inserting cards...")

cards_df.to_sql(
    name="cards",
    con=engine,
    schema="finflow_schema",
    if_exists="append",
    index=False,
    method="multi",
    chunksize=1000
)

print("Cards inserted successfully.")


# ============================================================
# VALIDATIONS
# ============================================================

print("\nRunning validations...")


validation_queries = {

    "total_cards": """
        SELECT COUNT(*) AS total_cards
        FROM finflow_schema.cards;
    """,

    "orphaned_customer_references": """
        SELECT COUNT(*) AS orphaned_customer_references
        FROM finflow_schema.cards c
        LEFT JOIN finflow_schema.customers cu
            ON c.customer_id = cu.customer_id
        WHERE cu.customer_id IS NULL;
    """,

    "orphaned_account_references": """
        SELECT COUNT(*) AS orphaned_account_references
        FROM finflow_schema.cards c
        LEFT JOIN finflow_schema.accounts a
            ON c.account_id = a.account_id
        WHERE a.account_id IS NULL;
    """,

    "invalid_customer_account_pairs": """
        SELECT COUNT(*) AS invalid_customer_account_pairs
        FROM finflow_schema.cards c
        JOIN finflow_schema.accounts a
            ON c.account_id = a.account_id
        WHERE c.customer_id <> a.customer_id;
    """,

    "duplicate_card_numbers": """
        SELECT COUNT(*) AS duplicate_card_numbers
        FROM (
            SELECT card_number
            FROM finflow_schema.cards
            GROUP BY card_number
            HAVING COUNT(*) > 1
        ) duplicates;
    """,

    "invalid_issue_dates": """
        SELECT COUNT(*) AS invalid_issue_dates
        FROM finflow_schema.cards c
        JOIN finflow_schema.accounts a
            ON c.account_id = a.account_id
        WHERE c.issued_at < a.opened_at;
    """,

    "invalid_expiration_dates": """
        SELECT COUNT(*) AS invalid_expiration_dates
        FROM finflow_schema.cards
        WHERE expires_at <= issued_at::date;
    """
}


with engine.connect() as connection:

    for validation_name, query in validation_queries.items():

        print(f"\n{validation_name}:")

        result = pd.read_sql(
            text(query),
            connection
        )

        print(result.to_string(index=False))