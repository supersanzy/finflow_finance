import random
from datetime import datetime, timedelta
from decimal import Decimal

import pandas as pd
from faker import Faker
from sqlalchemy import text

from data_generator.db_connection import connect_and_validate_db


# ==================================================
# CONFIGURATION
# ==================================================

MIN_NEW_CUSTOMERS = 2
MAX_NEW_CUSTOMERS = 3

CUSTOMER_BAD_DATA_RATE = 0.20


# ==================================================
# DATABASE CONNECTION
# ==================================================

engine = connect_and_validate_db()


# ==================================================
# FAKER
# ==================================================

fake = Faker("en_NG")


# ==================================================
# CUSTOMER CONFIGURATION
# ==================================================

customer_statuses = [
    "ACTIVE",
    "INACTIVE",
    "SUSPENDED"
]

status_weights = [
    0.85,
    0.10,
    0.05
]


# ==================================================
# NIGERIAN LOCATIONS
# ==================================================

nigerian_locations = {
    "Lagos": [
        "Ikeja",
        "Lekki",
        "Surulere",
        "Yaba",
        "Ikorodu"
    ],
    "Rivers": [
        "Port Harcourt",
        "Obio-Akpor",
        "Bonny"
    ],
    "Abuja": [
        "Garki",
        "Wuse",
        "Maitama",
        "Asokoro"
    ],
    "Anambra": [
        "Awka",
        "Onitsha",
        "Nnewi"
    ],
    "Enugu": [
        "Enugu",
        "Nsukka"
    ],
    "Oyo": [
        "Ibadan",
        "Ogbomosho"
    ],
    "Kano": [
        "Kano",
        "Wudil"
    ],
    "Edo": [
        "Benin City",
        "Ekpoma"
    ]
}


# ==================================================
# CITY STREETS
# ==================================================

city_streets = {
    "Ikeja": [
        "Allen Avenue",
        "Alausa Road",
        "Obafemi Awolowo Way"
    ],
    "Lekki": [
        "Admiralty Way",
        "Freedom Way",
        "Lekki-Epe Expressway"
    ],
    "Surulere": [
        "Adeniran Ogunsanya Street",
        "Bode Thomas Street",
        "Akinsanya Street"
    ],
    "Yaba": [
        "Herbert Macaulay Way",
        "Commercial Avenue",
        "Tejuosho Street"
    ],
    "Ikorodu": [
        "Ikorodu Road",
        "Lagos Road",
        "Ijede Road"
    ],
    "Port Harcourt": [
        "Aba Road",
        "Woji Road",
        "Peter Odili Road"
    ],
    "Obio-Akpor": [
        "East-West Road",
        "Rumuola Road",
        "Rumuokoro Road"
    ],
    "Bonny": [
        "Bonny Road",
        "Finima Road",
        "New Layout Road"
    ],
    "Garki": [
        "Ahmadu Bello Way",
        "Ladoke Akintola Boulevard",
        "Area 1 Road"
    ],
    "Wuse": [
        "Aminu Kano Crescent",
        "Adetokunbo Ademola Crescent",
        "Herbert Macaulay Way"
    ],
    "Maitama": [
        "Aguiyi Ironsi Street",
        "Yedseram Street",
        "Alfred Rewane Road"
    ],
    "Asokoro": [
        "Yakubu Gowon Crescent",
        "Justice Sowemimo Street",
        "Julius Nyerere Crescent"
    ],
    "Awka": [
        "Zik Avenue",
        "Nnamdi Azikiwe Road",
        "Arthur Eze Avenue"
    ],
    "Onitsha": [
        "Old Market Road",
        "Oguta Road",
        "Awka Road"
    ],
    "Nnewi": [
        "Nnewi-Nnobi Road",
        "Edoji Road",
        "Otolo Road"
    ],
    "Enugu": [
        "Ogui Road",
        "Chime Avenue",
        "Zik Avenue"
    ],
    "Nsukka": [
        "Ogige Road",
        "University Road",
        "Obachara Road"
    ],
    "Ibadan": [
        "Ring Road",
        "Bodija Road",
        "Mokola Hill Road"
    ],
    "Ogbomosho": [
        "Takie Square Road",
        "Oyo Road",
        "General Area Road"
    ],
    "Kano": [
        "Murtala Mohammed Way",
        "Zaria Road",
        "Bompai Road"
    ],
    "Wudil": [
        "Kano Road",
        "Wudil Main Road",
        "Gaya Road"
    ],
    "Benin City": [
        "Sapele Road",
        "Akpakpava Road",
        "Airport Road"
    ],
    "Ekpoma": [
        "Ekpoma-Auchi Road",
        "University Road",
        "Market Road"
    ]
}


# ==================================================
# RETRIEVE EXISTING EMAILS
# ==================================================

emails_query = """
SELECT email
FROM finflow_schema.customers
WHERE email IS NOT NULL
"""


existing_emails_df = pd.read_sql(
    emails_query,
    engine
)


used_emails = set(
    existing_emails_df["email"]
)


print(
    f"Existing emails loaded: "
    f"{len(used_emails)}"
)


# ==================================================
# GENERATE UNIQUE EMAIL
# ==================================================

def generate_email(first_name, last_name):

    domains = [
        "gmail.com",
        "yahoo.com",
        "outlook.com"
    ]

    base_email = (
        f"{first_name.lower()}."
        f"{last_name.lower()}"
    )

    domain = random.choice(domains)

    email = f"{base_email}@{domain}"

    counter = 1

    while email in used_emails:

        email = (
            f"{base_email}{counter}@{domain}"
        )

        counter += 1

    used_emails.add(email)

    return email


# ==================================================
# GENERATE NIGERIAN PHONE NUMBER
# ==================================================

def generate_nigerian_phone_number():

    prefixes = [
        "070",
        "080",
        "081",
        "090",
        "091"
    ]

    prefix = random.choice(prefixes)

    remaining_digits = "".join(
        str(random.randint(0, 9))
        for _ in range(8)
    )

    return f"{prefix}{remaining_digits}"


# ==================================================
# GENERATE ADDRESS
# ==================================================

def generate_address(city):

    house_number = random.randint(
        1,
        250
    )

    street = random.choice(
        city_streets[city]
    )

    return f"{house_number} {street}"


# ==================================================
# GENERATE INCREMENTAL CUSTOMERS
# ==================================================

def generate_new_customers(num_customers):

    customers = []

    current_time = datetime.now()

    for _ in range(num_customers):

        # ----------------------------------------------
        # GENERATE VALID CUSTOMER DATA
        # ----------------------------------------------

        gender = random.choice([
            "MALE",
            "FEMALE"
        ])

        if gender == "MALE":

            first_name = fake.first_name_male()

        else:

            first_name = fake.first_name_female()


        last_name = fake.last_name()


        email = generate_email(
            first_name,
            last_name
        )


        state = random.choice(
            list(nigerian_locations.keys())
        )


        city = random.choice(
            nigerian_locations[state]
        )


        country = "Nigeria"


        phone_number = (
            generate_nigerian_phone_number()
        )


        address = generate_address(
            city
        )


        # ----------------------------------------------
        # DATE OF BIRTH
        # ----------------------------------------------

        minimum_birth_date = (
            current_time
            - timedelta(days=75 * 365)
        ).date()


        maximum_birth_date = (
            current_time
            - timedelta(days=18 * 365)
        ).date()


        date_of_birth = fake.date_between(
            start_date=minimum_birth_date,
            end_date=maximum_birth_date
        )


        # ----------------------------------------------
        # CONTROLLED BAD DATA
        # ----------------------------------------------

        if random.random() < CUSTOMER_BAD_DATA_RATE:

            bad_data_type = random.choice([
                "MISSPELLED_GENDER",
                "INVALID_COUNTRY",
                "INVALID_STATE_CITY",
                "EMPTY_PHONE",
                "DUPLICATE_EMAIL",
                "EMPTY_ADDRESS"
            ])


            if bad_data_type == "MISSPELLED_GENDER":

                gender = "FEMALEE"


            elif bad_data_type == "INVALID_COUNTRY":

                country = "NIG"


            elif bad_data_type == "INVALID_STATE_CITY":

                # Awka belongs to Anambra,
                # but we deliberately assign it to Lagos

                state = "Lagos"
                city = "Awka"


            elif bad_data_type == "EMPTY_PHONE":

                phone_number = ""


            elif bad_data_type == "DUPLICATE_EMAIL":

                existing_email_choices = list(
                    used_emails
                )

                if existing_email_choices:

                    email = random.choice(
                        existing_email_choices
                    )


            elif bad_data_type == "EMPTY_ADDRESS":

                address = ""


        # ----------------------------------------------
        # CREATE CUSTOMER RECORD
        # ----------------------------------------------

        customer = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": phone_number,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "country": country,
            "state": state,
            "city": city,
            "address": address,
            "customer_status": random.choices(
                customer_statuses,
                weights=status_weights,
                k=1
            )[0],
            "created_at": current_time,
            "updated_at": None
        }


        customers.append(
            customer
        )


    return customers


# ==================================================
# GENERATE NEW CUSTOMERS
# ==================================================

num_new_customers = random.randint(
    MIN_NEW_CUSTOMERS,
    MAX_NEW_CUSTOMERS
)


print(
    f"\nGenerating "
    f"{num_new_customers} new customers..."
)


new_customers = generate_new_customers(
    num_new_customers
)


print(
    f"New customers generated: "
    f"{len(new_customers)}"
)

# ==================================================
# INSERT NEW CUSTOMERS
# ==================================================

print(
    "\nInserting new customers..."
)


insert_customers_query = text(
    """
    INSERT INTO finflow_schema.customers (
        first_name,
        last_name,
        email,
        phone_number,
        date_of_birth,
        gender,
        country,
        state,
        city,
        address,
        customer_status,
        created_at,
        updated_at
    )
    VALUES (
        :first_name,
        :last_name,
        :email,
        :phone_number,
        :date_of_birth,
        :gender,
        :country,
        :state,
        :city,
        :address,
        :customer_status,
        :created_at,
        :updated_at
    )
    RETURNING customer_id
    """
)


new_customer_ids = []


with engine.begin() as connection:

    for customer in new_customers:

        result = connection.execute(
            insert_customers_query,
            customer
        )

        customer_id = result.scalar()

        new_customer_ids.append(
            customer_id
        )


print(
    f"New customers inserted: "
    f"{len(new_customer_ids)}"
)


print(
    f"New customer IDs: "
    f"{new_customer_ids}"
)





# ==================================================
# RETRIEVE NEWLY CREATED CUSTOMERS
# ==================================================

new_customers_query = text(
    """
    SELECT
        customer_id,
        created_at
    FROM finflow_schema.customers
    WHERE customer_id = ANY(:customer_ids)
    """
)


with engine.connect() as connection:

    new_customers_df = pd.read_sql(
        new_customers_query,
        connection,
        params={
            "customer_ids": new_customer_ids
        }
    )


print(
    f"\nNew customers retrieved for accounts: "
    f"{len(new_customers_df)}"
)


# ==================================================
# ACCOUNT CONFIGURATION
# ==================================================

MIN_ACCOUNTS_PER_CUSTOMER = 1
MAX_ACCOUNTS_PER_CUSTOMER = 2

ACCOUNT_BAD_DATA_RATE = 0.20


account_types = [
    "SAVINGS",
    "CURRENT"
]


account_statuses = [
    "ACTIVE",
    "DORMANT",
    "CLOSED"
]


# ==================================================
# RETRIEVE EXISTING ACCOUNT NUMBERS
# ==================================================

account_numbers_query = """
SELECT account_number
FROM finflow_schema.accounts
WHERE account_number IS NOT NULL
"""


existing_account_numbers_df = pd.read_sql(
    account_numbers_query,
    engine
)


generated_account_numbers = set(
    existing_account_numbers_df["account_number"]
)


print(
    f"Existing account numbers loaded: "
    f"{len(generated_account_numbers)}"
)


# ==================================================
# GENERATE UNIQUE ACCOUNT NUMBER
# ==================================================

def generate_account_number():

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


# ==================================================
# GENERATE ACCOUNT OPENING DATE
# ==================================================

def generate_opened_at(customer_created_at):

    customer_created_at = (
        pd.Timestamp(customer_created_at)
        .to_pydatetime()
    )

    current_time = datetime.now()

    time_difference = (
        current_time
        - customer_created_at
    )

    total_seconds = int(
        time_difference.total_seconds()
    )

    if total_seconds <= 0:

        return customer_created_at


    random_seconds = random.randint(
        0,
        total_seconds
    )


    return (
        customer_created_at
        + timedelta(
            seconds=random_seconds
        )
    )


# ==================================================
# GENERATE ACCOUNT CLOSING DATE
# ==================================================

def generate_closed_at(
    account_status,
    opened_at
):

    if account_status != "CLOSED":

        return None


    current_time = datetime.now()

    time_difference = (
        current_time
        - opened_at
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
        + timedelta(
            seconds=random_seconds
        )
    )


# ==================================================
# GENERATE ACCOUNT BALANCE
# ==================================================

def generate_balance(account_status):

    if account_status == "CLOSED":

        return Decimal("0.00")


    balance = random.uniform(
        0,
        5_000_000
    )


    return Decimal(
        str(
            round(
                balance,
                2
            )
        )
    )


# ==================================================
# GENERATE INCREMENTAL ACCOUNTS
# ==================================================

accounts_data = []


for _, customer in new_customers_df.iterrows():

    customer_id = customer["customer_id"]

    customer_created_at = (
        customer["created_at"]
    )


    # Randomly assign 1 or 2 accounts

    number_of_accounts = random.randint(
        MIN_ACCOUNTS_PER_CUSTOMER,
        MAX_ACCOUNTS_PER_CUSTOMER
    )


    # Prevent duplicate account types
    # for the same customer

    selected_account_types = random.sample(
        account_types,
        k=number_of_accounts
    )


    for account_type in selected_account_types:

        # ----------------------------------------------
        # GENERATE VALID ACCOUNT
        # ----------------------------------------------

        account_status = random.choices(
            account_statuses,
            weights=[
                0.85,
                0.10,
                0.05
            ],
            k=1
        )[0]


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


        currency = "NGN"


        # ----------------------------------------------
        # CONTROLLED BAD DATA
        # ----------------------------------------------

        if random.random() < ACCOUNT_BAD_DATA_RATE:

            bad_data_type = random.choice([
                "WRONG_CURRENCY",
                "CLOSED_BEFORE_OPENED",
                "ACTIVE_WITH_CLOSED_DATE",
                "CLOSED_WITHOUT_CLOSED_DATE",
                "NEGATIVE_BALANCE"
            ])


            if bad_data_type == "WRONG_CURRENCY":

                currency = random.choice([
                    "USD",
                    "NIG"
                ])


            elif bad_data_type == "CLOSED_BEFORE_OPENED":

                closed_at = (
                    opened_at
                    - timedelta(
                        days=random.randint(
                            1,
                            30
                        )
                    )
                )


            elif bad_data_type == "ACTIVE_WITH_CLOSED_DATE":

                account_status = "ACTIVE"

                closed_at = (
                    opened_at
                    + timedelta(
                        days=1
                    )
                )


            elif bad_data_type == "CLOSED_WITHOUT_CLOSED_DATE":

                account_status = "CLOSED"

                closed_at = None


            elif bad_data_type == "NEGATIVE_BALANCE":

                balance = Decimal(
                    str(
                        -round(
                            random.uniform(
                                100,
                                100_000
                            ),
                            2
                        )
                    )
                )


        # ----------------------------------------------
        # CREATE ACCOUNT RECORD
        # ----------------------------------------------

        account = {
            "customer_id": customer_id,
            "account_number": generate_account_number(),
            "account_type": account_type,
            "currency": currency,
            "balance": balance,
            "account_status": account_status,
            "opened_at": opened_at,
            "closed_at": closed_at
        }


        accounts_data.append(
            account
        )


# ==================================================
# CREATE ACCOUNTS DATAFRAME
# ==================================================

accounts_df = pd.DataFrame(
    accounts_data
)


print(
    f"\nNew accounts generated: "
    f"{len(accounts_df)}"
)


# ==================================================
# INSERT INCREMENTAL ACCOUNTS
# ==================================================

print(
    "Inserting new accounts..."
)


accounts_df.to_sql(
    name="accounts",
    con=engine,
    schema="finflow_schema",
    if_exists="append",
    index=False,
    method="multi"
)


print(
    f"New accounts inserted: "
    f"{len(accounts_df)}"
)




# ==================================================
# TRANSACTION CONFIGURATION
# ==================================================

MIN_NEW_TRANSACTIONS = 5
MAX_NEW_TRANSACTIONS = 10

TRANSACTION_BAD_DATA_RATE = 0.20

TRANSACTION_TYPES = [
    "DEPOSIT",
    "BILL_PAYMENT",
    "WITHDRAWAL"
]

TRANSACTION_STATUSES = [
    "PENDING",
    "PROCESSING",
    "COMPLETED"
]

STATUS_WEIGHTS = [
    0.10,
    0.10,
    0.80
]

TRANSACTION_DIRECTIONS = [
    "CREDIT",
    "DEBIT"
]


# ==================================================
# RETRIEVE OLD ACTIVE ACCOUNTS
# ==================================================

old_accounts_query = """
SELECT
    account_id,
    opened_at
FROM finflow_schema.accounts
WHERE account_status = 'ACTIVE'
AND account_id NOT IN (
    SELECT account_id
    FROM finflow_schema.accounts
    WHERE customer_id = ANY(:customer_ids)
)
"""


with engine.connect() as connection:

    old_accounts_df = pd.read_sql(
        text(old_accounts_query),
        connection,
        params={
            "customer_ids": new_customer_ids
        }
    )


print(
    f"\nOld active accounts available: "
    f"{len(old_accounts_df)}"
)


# ==================================================
# RETRIEVE NEW ACCOUNTS
# ==================================================

new_accounts_query = """
SELECT
    account_id,
    opened_at
FROM finflow_schema.accounts
WHERE customer_id = ANY(:customer_ids)
"""


with engine.connect() as connection:

    new_accounts_df = pd.read_sql(
        text(new_accounts_query),
        connection,
        params={
            "customer_ids": new_customer_ids
        }
    )


print(
    f"New accounts available: "
    f"{len(new_accounts_df)}"
)


# ==================================================
# COMBINE OLD AND NEW ACCOUNTS
# ==================================================

available_accounts_df = pd.concat(
    [
        old_accounts_df,
        new_accounts_df
    ],
    ignore_index=True
)


print(
    f"Total accounts available for transactions: "
    f"{len(available_accounts_df)}"
)


# ==================================================
# RETRIEVE EXISTING TRANSACTION REFERENCES
# ==================================================

references_query = """
SELECT transaction_reference
FROM finflow_schema.transactions
WHERE transaction_reference IS NOT NULL
"""


existing_references_df = pd.read_sql(
    references_query,
    engine
)


used_transaction_references = set(
    existing_references_df[
        "transaction_reference"
    ]
)


print(
    f"Existing transaction references loaded: "
    f"{len(used_transaction_references)}"
)


# ==================================================
# GENERATE UNIQUE TRANSACTION REFERENCE
# ==================================================

def generate_transaction_reference():

    while True:

        reference = (
            f"TXN-"
            f"{random.randint(1000000000, 9999999999)}"
        )

        if reference not in used_transaction_references:

            used_transaction_references.add(
                reference
            )

            return reference


# ==================================================
# GENERATE TRANSACTION TIMESTAMP
# ==================================================

def generate_transaction_timestamp(account_opened_at):

    account_opened_at = (
        pd.Timestamp(account_opened_at)
        .to_pydatetime()
    )

    current_time = datetime.now()

    time_difference = (
        current_time
        - account_opened_at
    )

    total_seconds = int(
        time_difference.total_seconds()
    )

    if total_seconds <= 0:

        return account_opened_at


    random_seconds = random.randint(
        0,
        total_seconds
    )

    return (
        account_opened_at
        + timedelta(
            seconds=random_seconds
        )
    )


# ==================================================
# GENERATE TRANSACTION AMOUNT
# ==================================================

def generate_transaction_amount():

    amount = random.uniform(
        100,
        500_000
    )

    return Decimal(
        str(
            round(amount, 2)
        )
    )


# ==================================================
# GENERATE INCREMENTAL TRANSACTIONS
# ==================================================

num_new_transactions = random.randint(
    MIN_NEW_TRANSACTIONS,
    MAX_NEW_TRANSACTIONS
)


print(
    f"\nGenerating "
    f"{num_new_transactions} new transactions..."
)


base_transactions = []


for _ in range(num_new_transactions):

    selected_account = (
        available_accounts_df.sample(
            n=1
        ).iloc[0]
    )


    account_id = selected_account[
        "account_id"
    ]


    account_opened_at = selected_account[
        "opened_at"
    ]


    transaction_type = random.choice(
        TRANSACTION_TYPES
    )


    transaction_status = random.choices(
        TRANSACTION_STATUSES,
        weights=STATUS_WEIGHTS,
        k=1
    )[0]


    transaction_direction = random.choice(
        TRANSACTION_DIRECTIONS
    )


    amount = generate_transaction_amount()


    transaction_reference = (
        generate_transaction_reference()
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


    # ----------------------------------------------
    # CONTROLLED BAD DATA
    # ----------------------------------------------

    if random.random() < TRANSACTION_BAD_DATA_RATE:

        bad_data_type = random.choice([
            "TRANSACTION_AFTER_CREATED",
            "ZERO_AMOUNT",
            "NEGATIVE_AMOUNT",
            "DUPLICATE_REFERENCE"
        ])


        if bad_data_type == "TRANSACTION_AFTER_CREATED":

            transaction_at = (
                created_at
                + timedelta(
                    seconds=random.randint(
                        1,
                        300
                    )
                )
            )


        elif bad_data_type == "ZERO_AMOUNT":

            amount = Decimal("0.00")


        elif bad_data_type == "NEGATIVE_AMOUNT":

            amount = Decimal(
                str(
                    -round(
                        random.uniform(
                            100,
                            50_000
                        ),
                        2
                    )
                )
            )


        elif bad_data_type == "DUPLICATE_REFERENCE":

            if used_transaction_references:

                transaction_reference = random.choice(
                    list(
                        used_transaction_references
                    )
                )


    transaction = {
        "account_id": account_id,
        "transaction_reference": transaction_reference,
        "transaction_type": transaction_type,
        "transaction_status": transaction_status,
        "transaction_direction": transaction_direction,
        "amount": amount,
        "currency": "NGN",
        "original_transaction_id": None,
        "fee_for_transaction_id": None,
        "transaction_at": transaction_at,
        "created_at": created_at
    }


    base_transactions.append(
        transaction
    )


# ==================================================
# CREATE TRANSACTIONS DATAFRAME
# ==================================================

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
    con=engine,
    schema="finflow_schema",
    if_exists="append",
    index=False,
    method="multi"
)


print(
    f"Base transactions inserted: "
    f"{len(base_transactions_df)}"
)


# ==================================================
# RETRIEVE NEWLY INSERTED BASE TRANSACTIONS
# ==================================================

new_transaction_references = (
    base_transactions_df[
        "transaction_reference"
    ].tolist()
)


inserted_transactions_query = text(
    """
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
    WHERE transaction_reference = ANY(:references)
    """
)


with engine.connect() as connection:

    inserted_base_transactions_df = pd.read_sql(
        inserted_transactions_query,
        connection,
        params={
            "references": new_transaction_references
        }
    )


print(
    f"\nInserted base transactions retrieved: "
    f"{len(inserted_base_transactions_df)}"
)


# ==================================================
# SELECT ELIGIBLE DEBIT TRANSACTIONS
# ==================================================

eligible_fee_transactions_df = (
    inserted_base_transactions_df[
        inserted_base_transactions_df[
            "transaction_direction"
        ] == "DEBIT"
    ]
)


print(
    f"Eligible debit transactions for fees: "
    f"{len(eligible_fee_transactions_df)}"
)


# ==================================================
# FEE CONFIGURATION
# ==================================================

FEE_RATE = Decimal("0.01")

MIN_FEE = Decimal("10.00")

MAX_FEE = Decimal("500.00")

FEE_PROBABILITY = 0.70


# ==================================================
# GENERATE FEE TRANSACTIONS
# ==================================================

fee_transactions = []


for _, transaction in (
    eligible_fee_transactions_df.iterrows()
):

    # Not every debit transaction
    # necessarily has a fee.

    if random.random() > FEE_PROBABILITY:

        continue


    # Do not generate a fee for
    # invalid zero or negative amounts.

    if transaction["amount"] <= 0:

        continue


    fee_amount = (
        Decimal(
            str(transaction["amount"])
        )
        * FEE_RATE
    )


    # Apply minimum fee

    if fee_amount < MIN_FEE:

        fee_amount = MIN_FEE


    # Apply maximum fee

    if fee_amount > MAX_FEE:

        fee_amount = MAX_FEE


    fee_amount = fee_amount.quantize(
        Decimal("0.01")
    )


    fee_reference = (
        generate_transaction_reference()
    )


    fee_transaction = {
        "account_id": transaction["account_id"],
        "transaction_reference": fee_reference,
        "transaction_type": "FEE",
        "transaction_status": transaction[
            "transaction_status"
        ],
        "transaction_direction": "DEBIT",
        "amount": fee_amount,
        "currency": "NGN",
        "original_transaction_id": None,
        "fee_for_transaction_id": transaction[
            "transaction_id"
        ],
        "transaction_at": transaction[
            "transaction_at"
        ],
        "created_at": transaction[
            "created_at"
        ]
    }


    fee_transactions.append(
        fee_transaction
    )


print(
    f"Fee transactions generated: "
    f"{len(fee_transactions)}"
)


# ==================================================
# INSERT FEE TRANSACTIONS
# ==================================================

if fee_transactions:

    fee_transactions_df = pd.DataFrame(
        fee_transactions
    )


    print(
        "Inserting fee transactions..."
    )


    fee_transactions_df.to_sql(
        name="transactions",
        con=engine,
        schema="finflow_schema",
        if_exists="append",
        index=False,
        method="multi"
    )


    print(
        f"Fee transactions inserted: "
        f"{len(fee_transactions_df)}"
    )

else:

    print(
        "No eligible fee transactions "
        "generated this run."
    )