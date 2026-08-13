import random
from datetime import datetime, timedelta
from db_connection import connect_and_validate_db
from sqlalchemy import text


engine = connect_and_validate_db()

from faker import Faker


fake = Faker("en_NG")

NUM_CUSTOMERS = 10_000


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


used_emails = set()


def random_datetime(start_date, end_date):
    """
    Generate a random datetime between two datetime values.
    """

    time_difference = end_date - start_date

    random_seconds = random.randint(
        0,
        int(time_difference.total_seconds())
    )

    return start_date + timedelta(
        seconds=random_seconds
    )


def generate_email(first_name, last_name):
    """
    Generate a unique email based on the customer's name.
    """

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


def generate_nigerian_phone_number():
    """
    Generate a Nigerian mobile phone number.
    """

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


def generate_address(city):
    """
    Generate an address associated with the customer's city.
    """

    house_number = random.randint(1, 250)

    street = random.choice(
        city_streets[city]
    )

    return f"{house_number} {street}"


def generate_customers(num_customers=NUM_CUSTOMERS):
    """
    Generate synthetic Nigerian customer records.
    """

    customers = []

    start_created_at = datetime(
        2018,
        1,
        1
    )

    end_created_at = datetime(
        2026,
        7,
        31
    )

    for _ in range(num_customers):

        # Generate gender first
        gender = random.choice([
            "MALE",
            "FEMALE"
        ])

        # Generate a first name that matches the gender
        if gender == "MALE":
            first_name = fake.first_name_male()
        else:
            first_name = fake.first_name_female()

        last_name = fake.last_name()

        # Generate an email based on the customer's name
        email = generate_email(
            first_name,
            last_name
        )

        # Select a state and a city within that state
        state = random.choice(
            list(nigerian_locations.keys())
        )

        city = random.choice(
            nigerian_locations[state]
        )

        # Generate the date when the customer joined
        created_at = random_datetime(
            start_created_at,
            end_created_at
        )

        # Generate date of birth.
        # The customer must be between 18 and 75
        # when their record was created.
        minimum_birth_date = (
            created_at - timedelta(days=75 * 365)
        ).date()

        maximum_birth_date = (
            created_at - timedelta(days=18 * 365)
        ).date()

        date_of_birth = fake.date_between(
            start_date=minimum_birth_date,
            end_date=maximum_birth_date
        )

        # Some customer records have been updated
        updated_at = None

        if random.random() < 0.60:
            updated_at = random_datetime(
                created_at,
                end_created_at
            )

        customer = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": generate_nigerian_phone_number(),
            "date_of_birth": date_of_birth,
            "gender": gender,
            "country": "Nigeria",
            "state": state,
            "city": city,
            "address": generate_address(city),
            "customer_status": random.choices(
                customer_statuses,
                weights=status_weights,
                k=1
            )[0],
            "created_at": created_at,
            "updated_at": updated_at
        }

        customers.append(customer)

    return customers


def insert_customers(customers):
    """
    Truncate the customers table and insert generated customer records.
    """

    with engine.begin() as connection:

        connection.execute(
            text(
                """
                TRUNCATE TABLE finflow_schema.customers
                RESTART IDENTITY CASCADE;
                """
            )
        )

        connection.execute(
            text(
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
                """
            ),
            customers
        )

if __name__ == "__main__":

    customers = generate_customers()

    insert_customers(customers)

    print(f"{len(customers)} customers inserted successfully.")