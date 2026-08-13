import random

import pandas as pd
from sqlalchemy import text

from db_connection import connect_and_validate_db


engine = connect_and_validate_db()


# ============================================================
# CONFIGURATION
# ============================================================

MERCHANTS = {
    "GROCERY": [
        "Shoprite",
        "SPAR",
        "Market Square",
        "Justrite"
    ],

    "E_COMMERCE": [
        "Jumia",
        "Konga",
        "Jiji"
    ],

    "RESTAURANT": [
        "Chicken Republic",
        "Domino's Pizza",
        "The Place",
        "Cold Stone"
    ],

    "TRANSPORT": [
        "Bolt",
        "Uber",
        "ABC Transport"
    ],

    "TELECOMMUNICATIONS": [
        "MTN",
        "Airtel",
        "Glo",
        "9mobile"
    ],

    "FUEL": [
        "TotalEnergies",
        "Oando",
        "MRS"
    ],

    "ENTERTAINMENT": [
        "Netflix",
        "Spotify",
        "Filmhouse"
    ],

    "RETAIL": [
        "Miniso",
        "Mr Price",
        "Game"
    ]
}


# ============================================================
# RETRIEVE CARDS
# ============================================================

cards_query = text("""
    SELECT
        card_id,
        account_id,
        issued_at,
        expires_at
    FROM finflow_schema.cards
""")


with engine.connect() as connection:

    cards_df = pd.read_sql(
        cards_query,
        connection
    )


print(f"Cards retrieved: {len(cards_df)}")


if cards_df.empty:

    raise ValueError(
        "No cards found."
    )


# ============================================================
# RETRIEVE CARD PAYMENT TRANSACTIONS
# ============================================================

card_payments_query = text("""
    SELECT
        transaction_id,
        account_id,
        transaction_status,
        transaction_at,
        created_at
    FROM finflow_schema.transactions
    WHERE transaction_type = 'CARD_PAYMENT'
""")


with engine.connect() as connection:

    transactions_df = pd.read_sql(
        card_payments_query,
        connection
    )


print(
    f"Card payment transactions retrieved: "
    f"{len(transactions_df)}"
)


if transactions_df.empty:

    raise ValueError(
        "No CARD_PAYMENT transactions found."
    )


# ============================================================
# MATCH TRANSACTIONS TO VALID CARDS
# ============================================================

print("Matching transactions to cards...")


cards_by_account = (
    cards_df
    .groupby("account_id")["card_id"]
    .apply(list)
    .to_dict()
)


eligible_transactions = transactions_df[
    transactions_df["account_id"].isin(
        cards_by_account.keys()
    )
].copy()


print(
    f"Eligible card payment transactions: "
    f"{len(eligible_transactions)}"
)


# ============================================================
# GENERATE CARD TRANSACTIONS
# ============================================================

print("Generating card transactions...")


card_transactions = []


for _, transaction in eligible_transactions.iterrows():

    account_id = transaction["account_id"]

    available_cards = cards_by_account[
        account_id
    ]

    card_id = random.choice(
        available_cards
    )

    merchant_category = random.choice(
        list(MERCHANTS.keys())
    )

    merchant_name = random.choice(
        MERCHANTS[merchant_category]
    )

    card_transactions.append(
        {
            "card_id": int(card_id),
            "transaction_id": int(
                transaction["transaction_id"]
            ),
            "merchant_name": merchant_name,
            "merchant_category": merchant_category,
            "transaction_at": transaction[
                "transaction_at"
            ],
            "created_at": transaction[
                "created_at"
            ]
        }
    )


card_transactions_df = pd.DataFrame(
    card_transactions
)


print(
    f"Card transactions generated: "
    f"{len(card_transactions_df)}"
)


# ============================================================
# INSERT CARD TRANSACTIONS
# ============================================================

print("Inserting card transactions...")


card_transactions_df.to_sql(
    name="card_transactions",
    con=engine,
    schema="finflow_schema",
    if_exists="append",
    index=False,
    method="multi",
    chunksize=1000
)


print(
    "Card transactions inserted successfully."
)


# ============================================================
# VALIDATIONS
# ============================================================

print("\nRunning validations...")


validation_queries = {

    "total_card_transactions": """
        SELECT COUNT(*) AS total_card_transactions
        FROM finflow_schema.card_transactions;
    """,

    "orphaned_card_references": """
        SELECT COUNT(*) AS orphaned_card_references
        FROM finflow_schema.card_transactions ct
        LEFT JOIN finflow_schema.cards c
            ON ct.card_id = c.card_id
        WHERE c.card_id IS NULL;
    """,

    "orphaned_transaction_references": """
        SELECT COUNT(*) AS orphaned_transaction_references
        FROM finflow_schema.card_transactions ct
        LEFT JOIN finflow_schema.transactions t
            ON ct.transaction_id = t.transaction_id
        WHERE ct.transaction_id IS NOT NULL
        AND t.transaction_id IS NULL;
    """,

    "invalid_card_transaction_accounts": """
        SELECT COUNT(*) AS invalid_card_transaction_accounts
        FROM finflow_schema.card_transactions ct
        JOIN finflow_schema.cards c
            ON ct.card_id = c.card_id
        JOIN finflow_schema.transactions t
            ON ct.transaction_id = t.transaction_id
        WHERE c.account_id <> t.account_id;
    """,

    "invalid_transaction_types": """
        SELECT COUNT(*) AS invalid_transaction_types
        FROM finflow_schema.card_transactions ct
        JOIN finflow_schema.transactions t
            ON ct.transaction_id = t.transaction_id
        WHERE t.transaction_type <> 'CARD_PAYMENT';
    """,

    "invalid_transaction_timestamps": """
        SELECT COUNT(*) AS invalid_transaction_timestamps
        FROM finflow_schema.card_transactions ct
        JOIN finflow_schema.transactions t
            ON ct.transaction_id = t.transaction_id
        WHERE ct.transaction_at <> t.transaction_at;
    """,

    "future_card_transactions": """
        SELECT COUNT(*) AS future_card_transactions
        FROM finflow_schema.card_transactions
        WHERE transaction_at > CURRENT_TIMESTAMP;
    """
}


with engine.connect() as connection:

    for validation_name, query in validation_queries.items():

        print(f"\n{validation_name}:")

        result = pd.read_sql(
            text(query),
            connection
        )

        print(
            result.to_string(
                index=False
            )
        )