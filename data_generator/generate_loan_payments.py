import random
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

import pandas as pd
from sqlalchemy import text

from db_connection import connect_and_validate_db


engine = connect_and_validate_db()


# ============================================================
# CONFIGURATION
# ============================================================

BATCH_SIZE = 1000

PAYMENT_STATUS_WEIGHTS = {
    "COMPLETED": 0.90,
    "PENDING": 0.07,
    "PROCESSING": 0.03
}


# ============================================================
# RETRIEVE LOANS
# ============================================================

loans_query = text("""
    SELECT
        loan_id,
        account_id,
        loan_reference,
        loan_status,
        principal_amount,
        interest_rate,
        total_repayable_amount,
        outstanding_balance,
        term_months,
        disbursed_at,
        maturity_date
    FROM finflow_schema.loans
    WHERE disbursed_at IS NOT NULL
""")


with engine.connect() as connection:

    loans_df = pd.read_sql(
        loans_query,
        connection
    )


print(f"Loans retrieved: {len(loans_df)}")


if loans_df.empty:
    raise ValueError("No valid loans found.")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

used_payment_references = set()
used_transaction_references = set()


def generate_payment_reference():

    while True:

        reference = (
            f"LPY-"
            f"{random.randint(1000000000, 9999999999)}"
        )

        if reference not in used_payment_references:

            used_payment_references.add(reference)

            return reference


def generate_transaction_reference():

    while True:

        reference = (
            f"TXN-"
            f"{random.randint(1000000000, 9999999999)}"
        )

        if reference not in used_transaction_references:

            used_transaction_references.add(reference)

            return reference


def split_payment_amount(
    payment_amount,
    principal_remaining,
    interest_remaining
):

    payment_amount = Decimal(str(payment_amount))
    principal_remaining = Decimal(
        str(principal_remaining)
    )
    interest_remaining = Decimal(
        str(interest_remaining)
    )

    # Pay interest first, then principal.
    interest_amount = min(
        payment_amount,
        interest_remaining
    )

    principal_amount = (
        payment_amount - interest_amount
    )

    principal_amount = min(
        principal_amount,
        principal_remaining
    )

    actual_payment_amount = (
        principal_amount + interest_amount
    )

    return (
        actual_payment_amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        ),
        principal_amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        ),
        interest_amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )
    )


# ============================================================
# GENERATE LOAN PAYMENT DATA
# ============================================================

print("Generating loan payments...")


generated_payments = []

current_time = pd.Timestamp.now()


for _, loan in loans_df.iterrows():

    loan_id = int(loan["loan_id"])
    account_id = int(loan["account_id"])
    loan_status = loan["loan_status"]

    principal_amount = Decimal(
        str(loan["principal_amount"])
    )

    total_repayable = Decimal(
        str(loan["total_repayable_amount"])
    )

    outstanding_balance = Decimal(
        str(loan["outstanding_balance"])
    )

    disbursed_at = pd.Timestamp(
        loan["disbursed_at"]
    )

    maturity_date = pd.Timestamp(
        loan["maturity_date"]
    )

    # --------------------------------------------------------
    # Determine the historical amount already paid
    # --------------------------------------------------------

    total_paid = (
        total_repayable - outstanding_balance
    )

    if total_paid <= Decimal("0.00"):
        continue


    # --------------------------------------------------------
    # Determine number of payments
    # --------------------------------------------------------

    term_months = int(loan["term_months"])

    if loan_status == "PAID_OFF":

        max_payments = min(term_months, 12)

        num_payments = random.randint(
            max(2, max_payments // 2),
            max_payments
        )

    elif loan_status == "ACTIVE":

        max_payments = min(term_months, 8)

        num_payments = random.randint(
            1,
            max(1, max_payments)
        )

    elif loan_status == "DEFAULTED":

        max_payments = min(term_months, 6)

        num_payments = random.randint(
            1,
            max(1, max_payments)
        )

    else:

        num_payments = 1


    # --------------------------------------------------------
    # GENERATE PAYMENT AMOUNTS
    # --------------------------------------------------------

    remaining_to_allocate = total_paid

    payment_amounts = []


    for payment_number in range(num_payments):

        payments_remaining = (
            num_payments - payment_number
        )

        if payments_remaining == 1:

            payment_amount = remaining_to_allocate

        else:

            average_payment = (
                remaining_to_allocate
                / Decimal(payments_remaining)
            )

            lower_bound = (
                average_payment
                * Decimal("0.70")
            )

            upper_bound = (
                average_payment
                * Decimal("1.30")
            )

            payment_amount = Decimal(
                str(
                    random.uniform(
                        float(lower_bound),
                        float(upper_bound)
                    )
                )
            ).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )

            payment_amount = min(
                payment_amount,
                remaining_to_allocate
            )

        payment_amounts.append(
            payment_amount
        )

        remaining_to_allocate -= (
            payment_amount
        )


    # --------------------------------------------------------
    # GENERATE PAYMENT DATES
    # --------------------------------------------------------

    latest_payment_date = min(
        maturity_date,
        current_time
    )

    payment_period = (
        latest_payment_date
        - disbursed_at
    )

    if payment_period.total_seconds() <= 0:
        continue


    payment_dates = sorted(
        [
            disbursed_at
            + timedelta(
                seconds=random.randint(
                    1,
                    int(
                        payment_period.total_seconds()
                    )
                )
            )
            for _ in range(num_payments)
        ]
    )


    # --------------------------------------------------------
    # ALLOCATE PRINCIPAL AND INTEREST
    # --------------------------------------------------------

    total_interest = (
        total_repayable - principal_amount
    )

    remaining_principal = principal_amount
    remaining_interest = total_interest


    for payment_amount, payment_at in zip(
        payment_amounts,
        payment_dates
    ):

        (
            actual_payment_amount,
            principal_paid,
            interest_paid
        ) = split_payment_amount(
            payment_amount,
            remaining_principal,
            remaining_interest
        )

        remaining_principal -= principal_paid
        remaining_interest -= interest_paid


        payment_status = random.choices(
            population=list(
                PAYMENT_STATUS_WEIGHTS.keys()
            ),
            weights=list(
                PAYMENT_STATUS_WEIGHTS.values()
            ),
            k=1
        )[0]


        payment_reference = (
            generate_payment_reference()
        )

        transaction_reference = (
            generate_transaction_reference()
        )


        created_at = (
            payment_at
            + timedelta(
                seconds=random.randint(
                    0,
                    300
                )
            )
        )


        generated_payments.append(
            {
                "loan_id": loan_id,
                "account_id": account_id,

                "transaction_reference":
                    transaction_reference,

                "payment_reference":
                    payment_reference,

                "payment_amount":
                    actual_payment_amount,

                "principal_amount":
                    principal_paid,

                "interest_amount":
                    interest_paid,

                "payment_status":
                    payment_status,

                "payment_at":
                    payment_at,

                "created_at":
                    created_at,

                "loan_reference":
                    loan["loan_reference"]
            }
        )


# ============================================================
# CREATE DATAFRAME
# ============================================================

payments_df = pd.DataFrame(
    generated_payments
)


print(
    f"Loan payments generated: "
    f"{len(payments_df)}"
)


if payments_df.empty:

    raise ValueError(
        "No loan payments were generated."
    )


# ============================================================
# PREPARE TRANSACTIONS
# ============================================================

transactions_to_insert_df = pd.DataFrame(
    {
        "account_id":
            payments_df["account_id"],

        "transaction_reference":
            payments_df[
                "transaction_reference"
            ],

        "transaction_type":
            "LOAN_PAYMENT",

        "transaction_status":
            payments_df[
                "payment_status"
            ],

        "transaction_direction":
            "DEBIT",

        "amount":
            payments_df[
                "payment_amount"
            ],

        "currency":
            "NGN",

        "transaction_channel":
            "SYSTEM",

        "description":
            (
                "Loan repayment for "
                + payments_df[
                    "loan_reference"
                ]
            ),

        "original_transaction_id":
            None,

        "fee_for_transaction_id":
            None,

        "transaction_at":
            payments_df[
                "payment_at"
            ],

        "created_at":
            payments_df[
                "created_at"
            ]
    }
)


# ============================================================
# INSERT LOAN PAYMENT TRANSACTIONS
# ============================================================

print(
    "Inserting loan payment transactions..."
)


transactions_to_insert_df.to_sql(
    name="transactions",
    con=engine,
    schema="finflow_schema",
    if_exists="append",
    index=False,
    chunksize=BATCH_SIZE,
    method="multi"
)


print(
    "Loan payment transactions inserted successfully."
)


# ============================================================
# RETRIEVE EXACT INSERTED TRANSACTIONS
# ============================================================

print(
    "Retrieving inserted loan payment transactions..."
)


transaction_references = (
    payments_df[
        "transaction_reference"
    ].tolist()
)


inserted_transactions_query = text("""
    SELECT
        transaction_id,
        transaction_reference,
        account_id,
        amount,
        transaction_at,
        created_at
    FROM finflow_schema.transactions
    WHERE transaction_reference = ANY(:references)
""")


with engine.connect() as connection:

    inserted_transactions_df = pd.read_sql(
        inserted_transactions_query,
        connection,
        params={
            "references":
                transaction_references
        }
    )


print(
    f"Inserted loan payment transactions retrieved: "
    f"{len(inserted_transactions_df)}"
)


# ============================================================
# VALIDATE TRANSACTION RETRIEVAL
# ============================================================

if (
    len(inserted_transactions_df)
    != len(payments_df)
):

    raise ValueError(
        "Mismatch between generated loan payments "
        "and retrieved transactions."
    )


# ============================================================
# MATCH PAYMENTS TO TRANSACTIONS
# ============================================================

loan_payments_df = payments_df.merge(
    inserted_transactions_df[
        [
            "transaction_id",
            "transaction_reference"
        ]
    ],
    on="transaction_reference",
    how="inner",
    validate="one_to_one"
)


if len(loan_payments_df) != len(payments_df):

    raise ValueError(
        "Not all loan payments were matched "
        "to inserted transactions."
    )


# ============================================================
# PREPARE LOAN PAYMENTS FOR INSERTION
# ============================================================

loan_payments_to_insert_df = (
    loan_payments_df[
        [
            "loan_id",
            "transaction_id",
            "payment_reference",
            "payment_amount",
            "principal_amount",
            "interest_amount",
            "payment_status",
            "payment_at",
            "created_at"
        ]
    ]
)


# ============================================================
# INSERT LOAN PAYMENTS
# ============================================================

print("Inserting loan payments...")


loan_payments_to_insert_df.to_sql(
    name="loan_payments",
    con=engine,
    schema="finflow_schema",
    if_exists="append",
    index=False,
    chunksize=BATCH_SIZE,
    method="multi"
)


print(
    "Loan payments inserted successfully."
)


# ============================================================
# VALIDATIONS
# ============================================================

print("\nRunning validations...")


validation_queries = {

    "total_loan_payments": """
        SELECT COUNT(*) AS total_loan_payments
        FROM finflow_schema.loan_payments;
    """,

    "orphaned_loans": """
        SELECT COUNT(*) AS orphaned_loans
        FROM finflow_schema.loan_payments lp
        LEFT JOIN finflow_schema.loans l
            ON lp.loan_id = l.loan_id
        WHERE l.loan_id IS NULL;
    """,

    "orphaned_transactions": """
        SELECT COUNT(*) AS orphaned_transactions
        FROM finflow_schema.loan_payments lp
        LEFT JOIN finflow_schema.transactions t
            ON lp.transaction_id = t.transaction_id
        WHERE t.transaction_id IS NULL;
    """,

    "invalid_account_relationships": """
        SELECT COUNT(*) AS invalid_account_relationships
        FROM finflow_schema.loan_payments lp
        JOIN finflow_schema.loans l
            ON lp.loan_id = l.loan_id
        JOIN finflow_schema.transactions t
            ON lp.transaction_id = t.transaction_id
        WHERE l.account_id <> t.account_id;
    """,

    "invalid_transaction_types": """
        SELECT COUNT(*) AS invalid_transaction_types
        FROM finflow_schema.loan_payments lp
        JOIN finflow_schema.transactions t
            ON lp.transaction_id = t.transaction_id
        WHERE t.transaction_type <> 'LOAN_PAYMENT';
    """,

    "invalid_payment_amounts": """
        SELECT COUNT(*) AS invalid_payment_amounts
        FROM finflow_schema.loan_payments
        WHERE payment_amount <>
              principal_amount + interest_amount;
    """,

    "invalid_transaction_amounts": """
        SELECT COUNT(*) AS invalid_transaction_amounts
        FROM finflow_schema.loan_payments lp
        JOIN finflow_schema.transactions t
            ON lp.transaction_id = t.transaction_id
        WHERE lp.payment_amount <> t.amount;
    """,

    "invalid_payment_dates": """
        SELECT COUNT(*) AS invalid_payment_dates
        FROM finflow_schema.loan_payments lp
        JOIN finflow_schema.transactions t
            ON lp.transaction_id = t.transaction_id
        WHERE lp.payment_at <> t.transaction_at;
    """,

    "payments_before_disbursement": """
        SELECT COUNT(*) AS payments_before_disbursement
        FROM finflow_schema.loan_payments lp
        JOIN finflow_schema.loans l
            ON lp.loan_id = l.loan_id
        WHERE lp.payment_at < l.disbursed_at;
    """,

    "future_payments": """
        SELECT COUNT(*) AS future_payments
        FROM finflow_schema.loan_payments
        WHERE payment_at > CURRENT_TIMESTAMP;
    """,

    "duplicate_payment_references": """
        SELECT COUNT(*) AS duplicate_payment_references
        FROM (
            SELECT payment_reference
            FROM finflow_schema.loan_payments
            GROUP BY payment_reference
            HAVING COUNT(*) > 1
        ) duplicates;
    """,

    "duplicate_transaction_references": """
        SELECT COUNT(*) AS duplicate_transaction_references
        FROM (
            SELECT transaction_reference
            FROM finflow_schema.transactions
            WHERE transaction_type = 'LOAN_PAYMENT'
            GROUP BY transaction_reference
            HAVING COUNT(*) > 1
        ) duplicates;
    """
}


with engine.connect() as connection:

    for validation_name, query in (
        validation_queries.items()
    ):

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