import random
from datetime import datetime, timedelta
from db_connection import connect_and_validate_db
from sqlalchemy import create_engine, text



# ============================================================
# REFERENCE DATA
# ============================================================

FIRST_NAMES = [
    "Chinedu", "Emeka", "Obinna", "Ifeanyi", "Chukwuemeka",
    "Uche", "Kelechi", "Nnamdi", "Chisom", "Somtochukwu",
    "Adaeze", "Chioma", "Amaka", "Chiamaka", "Ngozi",
    "Nneka", "Ifeoma", "Ada", "Blessing", "Grace",
    "Daniel", "David", "Michael", "Samuel", "Joshua",
    "Esther", "Deborah", "Sarah", "Jennifer", "Mary"
]

LAST_NAMES = [
    "Okafor", "Okeke", "Eze", "Nwosu", "Nwachukwu",
    "Obi", "Umeh", "Ezeh", "Ibe", "Onyeka",
    "Agu", "Anyanwu", "Nnamani", "Ojukwu", "Ekwueme",
    "Ibekwe", "Chukwu", "Opara", "Okoro", "Nwankwo"
]

BANKS = [
    "Access Bank",
    "GTBank",
    "First Bank",
    "UBA",
    "Zenith Bank",
    "Fidelity Bank",
    "Union Bank",
    "Sterling Bank",
    "FCMB",
    "Stanbic IBTC",
    "Polaris Bank",
    "Wema Bank",
    "Ecobank"
]

STATUSES = [
    "ACTIVE",
    "ACTIVE",
    "ACTIVE",
    "ACTIVE",
    "INACTIVE"
]


# ============================================================
# DATA GENERATION
# ============================================================

def generate_beneficiaries(engine):

    with engine.connect() as conn:

        # ----------------------------------------------------
        # Retrieve existing customers
        # ----------------------------------------------------

        result = conn.execute(
            text("""
                SELECT customer_id
                FROM finflow_schema.customers
                ORDER BY customer_id
            """)
        )

        customer_ids = [row[0] for row in result]

        print(f"Customers retrieved: {len(customer_ids)}")

        if not customer_ids:
            print("No customers found. Cannot generate beneficiaries.")
            return

        # ----------------------------------------------------
        # Generate beneficiaries
        # ----------------------------------------------------

        beneficiaries = []

        for customer_id in customer_ids:

            # Each customer gets 0–5 beneficiaries
            number_of_beneficiaries = random.choices(
                [0, 1, 2, 3, 4, 5],
                weights=[5, 20, 30, 25, 15, 5],
                k=1
            )[0]

            used_accounts = set()

            for _ in range(number_of_beneficiaries):

                # Generate unique account number
                beneficiary_account = str(random.randint(
                    1000000000,
                    9999999999
                ))

                while beneficiary_account in used_accounts:
                    beneficiary_account = str(random.randint(
                        1000000000,
                        9999999999
                    ))

                used_accounts.add(beneficiary_account)

                beneficiary_name = (
                    f"{random.choice(FIRST_NAMES)} "
                    f"{random.choice(LAST_NAMES)}"
                )

                bank_name = random.choice(BANKS)

                status = random.choice(STATUSES)

                start_date = datetime(2022, 1, 1)
                end_date = datetime.now()

                days_range = (end_date - start_date).days

                created_at = start_date + timedelta(
                    days=random.randint(0, days_range)
                )

                beneficiaries.append({
                    "customer_id": customer_id,
                    "beneficiary_name": beneficiary_name,
                    "beneficiary_account": beneficiary_account,
                    "bank_name": bank_name,
                    "status": status,
                    "created_at": created_at
                })

        print(f"Beneficiaries generated: {len(beneficiaries)}")

        # ----------------------------------------------------
        # Insert beneficiaries
        # ----------------------------------------------------

        if beneficiaries:

            conn.execute(
                text("""
                    INSERT INTO finflow_schema.beneficiaries (
                        customer_id,
                        beneficiary_name,
                        beneficiary_account,
                        bank_name,
                        status,
                        created_at
                    )
                    VALUES (
                        :customer_id,
                        :beneficiary_name,
                        :beneficiary_account,
                        :bank_name,
                        :status,
                        :created_at
                    )
                """),
                beneficiaries
            )

            conn.commit()

        print("Beneficiaries inserted successfully.")


# ============================================================
# MAIN
# ============================================================

def main():

    engine = connect_and_validate_db()

    if engine:
        generate_beneficiaries(engine)


if __name__ == "__main__":
    main()