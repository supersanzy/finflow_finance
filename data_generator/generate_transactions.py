import random
from datetime import datetime, timedelta

import pandas as pd

from db_connection import connect_and_validate_db


# ==================================================
# CONFIGURATION
# ==================================================

NUM_BASE_TRANSACTIONS = 100_000

REVERSAL_RATE = 0.02
FEE_RATE = 0.20

BATCH_SIZE = 10_000


TRANSACTION_TYPES = [
    "DEPOSIT",
    "TRANSFER",
    "WITHDRAWAL",
    "BILL_PAYMENT",
    "CARD_PAYMENT"
]


TYPE_WEIGHTS = [
    0.15,   # DEPOSIT
    0.40,   # TRANSFER
    0.15,   # WITHDRAWAL
    0.15,   # BILL_PAYMENT
    0.15    # CARD_PAYMENT
]


STATUS_CHOICES = [
    "COMPLETED",
    "PROCESSING",
    "PENDING"
]


STATUS_WEIGHTS = [
    0.92,
    0.05,
    0.03
]


CHANNELS = {

    "DEPOSIT": [
        "BANK_TRANSFER",
        "BRANCH"
    ],

    "TRANSFER": [
        "MOBILE_APP",
        "WEB",
        "USSD"
    ],

    "WITHDRAWAL": [
        "ATM",
        "POS"
    ],

    "BILL_PAYMENT": [
        "MOBILE_APP",
        "WEB",
        "USSD"
    ],

    "CARD_PAYMENT": [
        "POS",
        "ONLINE"
    ]

}


DESCRIPTIONS = {

    "DEPOSIT": [
        "Account funding",
        "Bank transfer deposit",
        "Cash deposit"
    ],

    "TRANSFER": [
        "Funds transfer",
        "Transfer to beneficiary",
        "Account transfer"
    ],

    "WITHDRAWAL": [
        "Cash withdrawal",
        "ATM withdrawal"
    ],

    "BILL_PAYMENT": [
        "Utility bill payment",
        "Service payment",
        "Bill payment"
    ],

    "CARD_PAYMENT": [
        "Card purchase",
        "POS payment",
        "Online card payment"
    ]

}


# ==================================================
# DATABASE CONNECTION
# ==================================================

connection = connect_and_validate_db()


# ==================================================
# RETRIEVE ACCOUNTS
# ==================================================

accounts_query = """
SELECT
    account_id,
    opened_at
FROM finflow_schema.accounts
WHERE account_status != 'CLOSED'
AND opened_at IS NOT NULL
"""


accounts_df = pd.read_sql(
    accounts_query,
    connection
)


print(
    f"Accounts retrieved: {len(accounts_df)}"
)


if accounts_df.empty:

    raise ValueError(
        "No valid accounts found."
    )


accounts_df["opened_at"] = pd.to_datetime(
    accounts_df["opened_at"]
)


account_ids = accounts_df[
    "account_id"
].tolist()


account_opened_dates = accounts_df[
    "opened_at"
].tolist()


# ==================================================
# GENERATE UNIQUE TRANSACTION REFERENCES
# ==================================================

used_references = set()


def generate_transaction_reference():

    while True:

        reference = (
            f"TXN-"
            f"{random.randint(1000000000, 9999999999)}"
        )

        if reference not in used_references:

            used_references.add(
                reference
            )

            return reference


# ==================================================
# GENERATE TRANSACTION AMOUNT
# ==================================================

def generate_amount(
    transaction_type
):

    amount_ranges = {

        "DEPOSIT": (
            1_000,
            1_000_000
        ),

        "TRANSFER": (
            500,
            500_000
        ),

        "WITHDRAWAL": (
            1_000,
            200_000
        ),

        "BILL_PAYMENT": (
            500,
            250_000
        ),

        "CARD_PAYMENT": (
            500,
            300_000
        )

    }


    minimum, maximum = (
        amount_ranges[
            transaction_type
        ]
    )


    amount = random.uniform(
        minimum,
        maximum
    )


    return round(
        amount,
        2
    )


# ==================================================
# GENERATE TRANSACTION DIRECTION
# ==================================================

def generate_direction(
    transaction_type
):

    if transaction_type == "DEPOSIT":

        return "CREDIT"


    if transaction_type == "TRANSFER":

        return random.choice(
            [
                "DEBIT",
                "CREDIT"
            ]
        )


    return "DEBIT"


# ==================================================
# GENERATE TRANSACTION TIMESTAMP
# ==================================================

def generate_transaction_timestamp(
    account_opened_at
):

    current_time = datetime.now()


    maximum_transaction_time = min(
        account_opened_at
        + timedelta(days=365 * 3),
        current_time
    )


    time_difference = (
        maximum_transaction_time
        - account_opened_at
    )


    total_seconds = int(
        time_difference.total_seconds()
    )


    if total_seconds <= 0:

        return account_opened_at


    random_seconds = random.randint(
        1,
        total_seconds
    )


    return (
        account_opened_at
        + timedelta(
            seconds=random_seconds
        )
    )


# ==================================================
# GENERATE BASE TRANSACTIONS
# ==================================================

print(
    "Generating base transactions..."
)


base_transactions = []


for _ in range(
    NUM_BASE_TRANSACTIONS
):

    account_index = random.randrange(
        len(account_ids)
    )


    account_id = account_ids[
        account_index
    ]


    account_opened_at = (
        account_opened_dates[
            account_index
        ]
    )


    transaction_type = random.choices(
        TRANSACTION_TYPES,
        weights=TYPE_WEIGHTS,
        k=1
    )[0]


    transaction_status = random.choices(
        STATUS_CHOICES,
        weights=STATUS_WEIGHTS,
        k=1
    )[0]


    transaction_direction = (
        generate_direction(
            transaction_type
        )
    )


    amount = generate_amount(
        transaction_type
    )


    transaction_channel = random.choice(
        CHANNELS[
            transaction_type
        ]
    )


    transaction_at = (
        generate_transaction_timestamp(
            account_opened_at
        )
    )


    created_at = (
        transaction_at
        + timedelta(
            seconds=random.randint(
                0,
                300
            )
        )
    )


    base_transactions.append(
        {

            "account_id":
                account_id,

            "transaction_reference":
                generate_transaction_reference(),

            "transaction_type":
                transaction_type,

            "transaction_status":
                transaction_status,

            "transaction_direction":
                transaction_direction,

            "amount":
                amount,

            "currency":
                "NGN",

            "transaction_channel":
                transaction_channel,

            "description":
                random.choice(
                    DESCRIPTIONS[
                        transaction_type
                    ]
                ),

            "original_transaction_id":
                None,

            "fee_for_transaction_id":
                None,

            "transaction_at":
                transaction_at,

            "created_at":
                created_at

        }
    )


base_transactions_df = pd.DataFrame(
    base_transactions
)


print(
    f"Base transactions generated: "
    f"{len(base_transactions_df)}"
)


# ==================================================
# INSERT BASE TRANSACTIONS
# ==================================================

print(
    "Inserting base transactions..."
)


base_transactions_df.to_sql(
    name="transactions",
    con=connection,
    schema="finflow_schema",
    if_exists="append",
    index=False,
    chunksize=BATCH_SIZE,
    method="multi"
)


print(
    "Base transactions inserted successfully."
)


# ==================================================
# RETRIEVE BASE TRANSACTIONS
# ==================================================

print(
    "Retrieving inserted transactions..."
)


base_transactions_query = """
SELECT
    transaction_id,
    account_id,
    transaction_reference,
    transaction_type,
    transaction_status,
    transaction_direction,
    amount,
    transaction_at,
    created_at
FROM finflow_schema.transactions
WHERE original_transaction_id IS NULL
AND fee_for_transaction_id IS NULL
"""


inserted_transactions_df = pd.read_sql(
    base_transactions_query,
    connection
)


print(
    f"Transactions available for relationships: "
    f"{len(inserted_transactions_df)}"
)


# ==================================================
# GENERATE REVERSAL TRANSACTIONS
# ==================================================

print(
    "Generating reversal transactions..."
)


eligible_for_reversal = (
    inserted_transactions_df[
        inserted_transactions_df[
            "transaction_status"
        ]
        == "COMPLETED"
    ]
)


num_reversals = int(
    len(eligible_for_reversal)
    * REVERSAL_RATE
)


reversal_source_df = (
    eligible_for_reversal.sample(
        n=num_reversals,
        replace=False
    )
)


reversal_transactions = []


for _, transaction in (
    reversal_source_df.iterrows()
):

    if (
        transaction[
            "transaction_direction"
        ]
        == "DEBIT"
    ):

        reversal_direction = "CREDIT"

    else:

        reversal_direction = "DEBIT"


    # ----------------------------------------------
    # Generate reversal timestamp
    # ----------------------------------------------

    original_transaction_at = pd.Timestamp(
        transaction[
            "transaction_at"
        ]
    )


    current_time = pd.Timestamp.now()


    maximum_reversal_time = min(
        original_transaction_at
        + timedelta(hours=24),
        current_time
    )


    time_difference = (
        maximum_reversal_time
        - original_transaction_at
    )


    total_seconds = int(
        time_difference.total_seconds()
    )


    if total_seconds > 1:

        reversal_seconds = random.randint(
            1,
            total_seconds
        )


        transaction_at = (
            original_transaction_at
            + timedelta(
                seconds=reversal_seconds
            )
        )

    else:

        transaction_at = (
            original_transaction_at
            + timedelta(seconds=1)
        )


    created_at = (
        transaction_at
        + timedelta(
            seconds=random.randint(
                0,
                300
            )
        )
    )


    reversal_transactions.append(
        {

            "account_id":
                transaction[
                    "account_id"
                ],

            "transaction_reference":
                generate_transaction_reference(),

            "transaction_type":
                "REVERSAL",

            "transaction_status":
                "REVERSED",

            "transaction_direction":
                reversal_direction,

            "amount":
                transaction[
                    "amount"
                ],

            "currency":
                "NGN",

            "transaction_channel":
                "SYSTEM",

            "description":
                (
                    "Reversal of transaction "
                    f"{transaction['transaction_reference']}"
                ),

            "original_transaction_id":
                transaction[
                    "transaction_id"
                ],

            "fee_for_transaction_id":
                None,

            "transaction_at":
                transaction_at,

            "created_at":
                created_at

        }
    )


reversal_transactions_df = pd.DataFrame(
    reversal_transactions
)


print(
    f"Reversal transactions generated: "
    f"{len(reversal_transactions_df)}"
)


# ==================================================
# INSERT REVERSAL TRANSACTIONS
# ==================================================

if not reversal_transactions_df.empty:

    print(
        "Inserting reversal transactions..."
    )


    reversal_transactions_df.to_sql(
        name="transactions",
        con=connection,
        schema="finflow_schema",
        if_exists="append",
        index=False,
        chunksize=BATCH_SIZE,
        method="multi"
    )


    print(
        "Reversal transactions inserted successfully."
    )


# ==================================================
# GENERATE FEE TRANSACTIONS
# ==================================================

print(
    "Generating fee transactions..."
)


fee_eligible_types = [
    "TRANSFER",
    "WITHDRAWAL",
    "BILL_PAYMENT",
    "CARD_PAYMENT"
]


eligible_for_fee = (
    inserted_transactions_df[
        (
            inserted_transactions_df[
                "transaction_direction"
            ]
            == "DEBIT"
        )
        &
        (
            inserted_transactions_df[
                "transaction_type"
            ].isin(
                fee_eligible_types
            )
        )
        &
        (
            inserted_transactions_df[
                "transaction_status"
            ]
            == "COMPLETED"
        )
    ]
)


num_fees = int(
    len(eligible_for_fee)
    * FEE_RATE
)


fee_source_df = (
    eligible_for_fee.sample(
        n=num_fees,
        replace=False
    )
)


fee_transactions = []


for _, transaction in (
    fee_source_df.iterrows()
):

    percentage_fee = float(
        transaction["amount"]
    ) * random.uniform(
        0.001,
        0.005
    )


    fee_amount = min(
        max(
            round(
                percentage_fee,
                2
            ),
            10
        ),
        500
    )


    transaction_at = (
        pd.Timestamp(
            transaction[
                "transaction_at"
            ]
        )
        + timedelta(
            seconds=random.randint(
                1,
                120
            )
        )
    )


    created_at = (
        transaction_at
        + timedelta(
            seconds=random.randint(
                0,
                120
            )
        )
    )


    fee_transactions.append(
        {

            "account_id":
                transaction[
                    "account_id"
                ],

            "transaction_reference":
                generate_transaction_reference(),

            "transaction_type":
                "FEE",

            "transaction_status":
                "COMPLETED",

            "transaction_direction":
                "DEBIT",

            "amount":
                fee_amount,

            "currency":
                "NGN",

            "transaction_channel":
                "SYSTEM",

            "description":
                (
                    "Transaction fee for "
                    f"{transaction['transaction_reference']}"
                ),

            "original_transaction_id":
                None,

            "fee_for_transaction_id":
                transaction[
                    "transaction_id"
                ],

            "transaction_at":
                transaction_at,

            "created_at":
                created_at

        }
    )


fee_transactions_df = pd.DataFrame(
    fee_transactions
)


print(
    f"Fee transactions generated: "
    f"{len(fee_transactions_df)}"
)


# ==================================================
# INSERT FEE TRANSACTIONS
# ==================================================

if not fee_transactions_df.empty:

    print(
        "Inserting fee transactions..."
    )


    fee_transactions_df.to_sql(
        name="transactions",
        con=connection,
        schema="finflow_schema",
        if_exists="append",
        index=False,
        chunksize=BATCH_SIZE,
        method="multi"
    )


    print(
        "Fee transactions inserted successfully."
    )


# ==================================================
# VALIDATIONS
# ==================================================

print(
    "\nRunning validations..."
)


validation_queries = {

    "total_transactions": """
        SELECT COUNT(*) AS total_transactions
        FROM finflow_schema.transactions;
    """,

    "orphaned_accounts": """
        SELECT COUNT(*) AS orphaned_accounts
        FROM finflow_schema.transactions t
        LEFT JOIN finflow_schema.accounts a
            ON t.account_id = a.account_id
        WHERE a.account_id IS NULL;
    """,

    "invalid_original_transactions": """
        SELECT COUNT(*) AS invalid_original_transactions
        FROM finflow_schema.transactions t
        LEFT JOIN finflow_schema.transactions o
            ON t.original_transaction_id = o.transaction_id
        WHERE t.original_transaction_id IS NOT NULL
        AND o.transaction_id IS NULL;
    """,

    "invalid_fee_transactions": """
        SELECT COUNT(*) AS invalid_fee_transactions
        FROM finflow_schema.transactions t
        LEFT JOIN finflow_schema.transactions f
            ON t.fee_for_transaction_id = f.transaction_id
        WHERE t.fee_for_transaction_id IS NOT NULL
        AND f.transaction_id IS NULL;
    """,

    "invalid_reversal_direction": """
        SELECT COUNT(*) AS invalid_reversal_direction
        FROM finflow_schema.transactions r
        JOIN finflow_schema.transactions o
            ON r.original_transaction_id = o.transaction_id
        WHERE r.transaction_direction =
              o.transaction_direction;
    """,

    "invalid_reversal_amount": """
        SELECT COUNT(*) AS invalid_reversal_amount
        FROM finflow_schema.transactions r
        JOIN finflow_schema.transactions o
            ON r.original_transaction_id = o.transaction_id
        WHERE r.amount <> o.amount;
    """,

    "invalid_reversal_dates": """
        SELECT COUNT(*) AS invalid_reversal_dates
        FROM finflow_schema.transactions r
        JOIN finflow_schema.transactions o
            ON r.original_transaction_id = o.transaction_id
        WHERE r.transaction_at <= o.transaction_at;
    """,

    "invalid_transaction_dates": """
        SELECT COUNT(*) AS invalid_transaction_dates
        FROM finflow_schema.transactions
        WHERE transaction_at > created_at;
    """,

    "future_transactions": """
        SELECT COUNT(*) AS future_transactions
        FROM finflow_schema.transactions
        WHERE transaction_at > CURRENT_TIMESTAMP;
    """,

    "duplicate_transaction_references": """
        SELECT COUNT(*) AS duplicate_transaction_references
        FROM (
            SELECT transaction_reference
            FROM finflow_schema.transactions
            GROUP BY transaction_reference
            HAVING COUNT(*) > 1
        ) duplicates;
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

total_generated = (
    len(base_transactions_df)
    + len(reversal_transactions_df)
    + len(fee_transactions_df)
)


print(
    "\n"
    "=" * 50
)


print(
    "TRANSACTION GENERATION COMPLETE"
)


print(
    "=" * 50
)


print(
    f"Base transactions: "
    f"{len(base_transactions_df)}"
)


print(
    f"Reversal transactions: "
    f"{len(reversal_transactions_df)}"
)


print(
    f"Fee transactions: "
    f"{len(fee_transactions_df)}"
)


print(
    f"Total generated: "
    f"{total_generated}"
)


# ==================================================
# DISPOSE DATABASE ENGINE
# ==================================================

connection.dispose()