import random

import pandas as pd

from db_connection import connect_and_validate_db


# ==================================================
# CONFIGURATION
# ==================================================

BATCH_SIZE = 10_000


TRANSFER_METHODS = [
    "BANK_TRANSFER",
    "INTERNAL_TRANSFER"
]


TRANSFER_METHOD_WEIGHTS = [
    0.90,
    0.10
]


TRANSFER_PURPOSES = [
    "Personal transfer",
    "Family support",
    "Rent payment",
    "School fees",
    "Business payment",
    "Loan repayment",
    "Savings",
    "Gift",
    "Emergency support",
    "Other"
]


# ==================================================
# DATABASE CONNECTION
# ==================================================

connection = connect_and_validate_db()


# ==================================================
# RETRIEVE ELIGIBLE TRANSFER TRANSACTIONS
# ==================================================

eligible_transfers_query = """
SELECT
    t.transaction_id,
    t.account_id,
    t.transaction_at,
    t.created_at,
    a.customer_id
FROM finflow_schema.transactions t
JOIN finflow_schema.accounts a
    ON t.account_id = a.account_id
WHERE t.transaction_type = 'TRANSFER'
AND t.transaction_direction = 'DEBIT'
AND t.transaction_status = 'COMPLETED';
"""


eligible_transfers_df = pd.read_sql(
    eligible_transfers_query,
    connection
)


print(
    f"Eligible sender transactions: "
    f"{len(eligible_transfers_df)}"
)


if eligible_transfers_df.empty:

    raise ValueError(
        "No eligible sender transactions found."
    )


# ==================================================
# RETRIEVE BENEFICIARIES
# ==================================================

beneficiaries_query = """
SELECT
    beneficiary_id,
    customer_id
FROM finflow_schema.beneficiaries
WHERE status = 'ACTIVE';
"""


beneficiaries_df = pd.read_sql(
    beneficiaries_query,
    connection
)


print(
    f"Active beneficiaries retrieved: "
    f"{len(beneficiaries_df)}"
)


if beneficiaries_df.empty:

    raise ValueError(
        "No active beneficiaries found."
    )


# ==================================================
# IDENTIFY CUSTOMERS WITH BENEFICIARIES
# ==================================================

beneficiaries_by_customer = (
    beneficiaries_df
    .groupby("customer_id")["beneficiary_id"]
    .apply(list)
    .to_dict()
)


# ==================================================
# FILTER ELIGIBLE TRANSFERS
# ==================================================

eligible_transfers_df = (
    eligible_transfers_df[
        eligible_transfers_df["customer_id"].isin(
            beneficiaries_by_customer.keys()
        )
    ]
)


print(
    f"Eligible transfers with beneficiaries: "
    f"{len(eligible_transfers_df)}"
)


if eligible_transfers_df.empty:

    raise ValueError(
        "No eligible transfers found for customers "
        "with beneficiaries."
    )


# ==================================================
# GENERATE UNIQUE TRANSFER REFERENCES
# ==================================================

used_references = set()


def generate_transfer_reference():

    while True:

        reference = (
            f"TRF-"
            f"{random.randint(1000000000, 9999999999)}"
        )

        if reference not in used_references:

            used_references.add(
                reference
            )

            return reference


# ==================================================
# GENERATE TRANSFERS
# ==================================================

print(
    "Generating transfers..."
)


transfers = []


for _, transaction in (
    eligible_transfers_df.iterrows()
):

    customer_id = (
        transaction["customer_id"]
    )


    available_beneficiaries = (
        beneficiaries_by_customer[
            customer_id
        ]
    )


    beneficiary_id = random.choice(
        available_beneficiaries
    )


    transfer_method = random.choices(
        TRANSFER_METHODS,
        weights=TRANSFER_METHOD_WEIGHTS,
        k=1
    )[0]


    transfer_purpose = random.choice(
        TRANSFER_PURPOSES
    )


    transfers.append(
        {

            "transfer_reference":
                generate_transfer_reference(),

            "sender_transaction_id":
                transaction["transaction_id"],

            "receiver_transaction_id":
                None,

            "beneficiary_id":
                beneficiary_id,

            "transfer_method":
                transfer_method,

            "transfer_purpose":
                transfer_purpose,

            "created_at":
                transaction["created_at"]

        }
    )


transfers_df = pd.DataFrame(
    transfers
)


print(
    f"Transfers generated: "
    f"{len(transfers_df)}"
)


# ==================================================
# INSERT TRANSFERS
# ==================================================

print(
    "Inserting transfers..."
)


transfers_df.to_sql(
    name="transfers",
    con=connection,
    schema="finflow_schema",
    if_exists="append",
    index=False,
    chunksize=BATCH_SIZE,
    method="multi"
)


print(
    "Transfers inserted successfully."
)


# ==================================================
# VALIDATIONS
# ==================================================

print(
    "\nRunning validations..."
)


validation_queries = {

    "total_transfers": """
        SELECT COUNT(*) AS total_transfers
        FROM finflow_schema.transfers;
    """,

    "orphaned_sender_transactions": """
        SELECT COUNT(*) AS orphaned_sender_transactions
        FROM finflow_schema.transfers tr
        LEFT JOIN finflow_schema.transactions t
            ON tr.sender_transaction_id = t.transaction_id
        WHERE t.transaction_id IS NULL;
    """,

    "invalid_sender_transactions": """
        SELECT COUNT(*) AS invalid_sender_transactions
        FROM finflow_schema.transfers tr
        JOIN finflow_schema.transactions t
            ON tr.sender_transaction_id = t.transaction_id
        WHERE t.transaction_type != 'TRANSFER'
        OR t.transaction_direction != 'DEBIT'
        OR t.transaction_status != 'COMPLETED';
    """,

    "orphaned_beneficiaries": """
        SELECT COUNT(*) AS orphaned_beneficiaries
        FROM finflow_schema.transfers tr
        LEFT JOIN finflow_schema.beneficiaries b
            ON tr.beneficiary_id = b.beneficiary_id
        WHERE tr.beneficiary_id IS NOT NULL
        AND b.beneficiary_id IS NULL;
    """,

    "beneficiary_customer_mismatch": """
        SELECT COUNT(*) AS beneficiary_customer_mismatch
        FROM finflow_schema.transfers tr
        JOIN finflow_schema.transactions t
            ON tr.sender_transaction_id = t.transaction_id
        JOIN finflow_schema.accounts a
            ON t.account_id = a.account_id
        JOIN finflow_schema.beneficiaries b
            ON tr.beneficiary_id = b.beneficiary_id
        WHERE a.customer_id != b.customer_id;
    """,

    "duplicate_transfer_references": """
        SELECT COUNT(*) AS duplicate_transfer_references
        FROM (
            SELECT transfer_reference
            FROM finflow_schema.transfers
            GROUP BY transfer_reference
            HAVING COUNT(*) > 1
        ) duplicates;
    """,

    "duplicate_sender_transactions": """
        SELECT COUNT(*) AS duplicate_sender_transactions
        FROM (
            SELECT sender_transaction_id
            FROM finflow_schema.transfers
            GROUP BY sender_transaction_id
            HAVING COUNT(*) > 1
        ) duplicates;
    """,

    "invalid_transfer_dates": """
        SELECT COUNT(*) AS invalid_transfer_dates
        FROM finflow_schema.transfers tr
        JOIN finflow_schema.transactions t
            ON tr.sender_transaction_id = t.transaction_id
        WHERE tr.created_at < t.transaction_at;
    """

}


for validation_name, query in (
    validation_queries.items()
):

    result = pd.read_sql(
        query,
        connection
    )


    print(
        f"\n{validation_name}:"
    )


    print(
        result.to_string(
            index=False
        )
    )


# ==================================================
# FINAL SUMMARY
# ==================================================

print(
    "\n"
    + "=" * 50
)


print(
    "TRANSFER GENERATION COMPLETE"
)


print(
    "=" * 50
)


print(
    f"Transfers generated: "
    f"{len(transfers_df)}"
)


# ==================================================
# DISPOSE DATABASE ENGINE
# ==================================================

connection.dispose()