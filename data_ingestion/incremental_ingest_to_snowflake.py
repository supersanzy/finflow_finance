from data_generator.db_connection import connect_and_validate_db
from data_ingestion.snowflake_python import sf_connect
import pandas as pd
from sqlalchemy import text
from snowflake.connector.pandas_tools import write_pandas


engine = connect_and_validate_db()
sf_conn = sf_connect()
schema = "FINFLOW_SCHEMA"


def get_last_loaded_id(conn, table_name, id_column):
    cursor = conn.cursor()
    query = f"""
        SELECT MAX({id_column})
        FROM {schema}.{table_name}
    """
    cursor.execute(query)
    last_loaded_id = cursor.fetchone()[0]

    return last_loaded_id if last_loaded_id is not None else 0



cust_last_loaded_id = get_last_loaded_id(
    sf_conn,
    "CUSTOMERS",
    "CUSTOMER_ID"
)

# print(cust_last_loaded_id)

transactions_last_loaded_id = get_last_loaded_id(
    sf_conn,
    "TRANSACTIONS",
    "TRANSACTION_ID"
)

# # print(transactions_last_loaded_id)

accts_last_loaded_id = get_last_loaded_id(
    sf_conn,
    "ACCOUNTS",
    "ACCOUNT_ID"
)

# print(accts_last_loaded_id)

customer_query = text("""
    SELECT *
    FROM finflow_schema.customers
    WHERE customer_id > :last_loaded_id
""")

account_query = text("""
    SELECT *
    FROM finflow_schema.accounts
    WHERE account_id > :last_loaded_id
""")

transaction_query = text("""
    SELECT *
    FROM finflow_schema.transactions
    WHERE transaction_id > :last_loaded_id
""")


with engine.connect() as pg_conn:
    customers_df = pd.read_sql(
        customer_query,
        con=pg_conn,
        params={"last_loaded_id": cust_last_loaded_id}
    )

if not customers_df.empty:
    customers_df.columns = customers_df.columns.str.upper()

    success, nchunks, nrows, output = write_pandas(
        conn=sf_conn,
        df=customers_df,
        table_name="CUSTOMERS",
        schema="FINFLOW_SCHEMA"
    )
    print(f"Rows loaded: {nrows}")

else:
    print("No new accounts to load.")



# Ingest Accounts Table Incrementally to SNowflake

with engine.connect() as pg_conn:
    accounts_df = pd.read_sql(
        account_query,
        con=pg_conn,
        params={"last_loaded_id": accts_last_loaded_id}
    )

if not accounts_df.empty:
    accounts_df.columns = accounts_df.columns.str.upper()
    success, nchunks, nrows, output = write_pandas(
        conn=sf_conn,
        df=accounts_df,
        table_name="ACCOUNTS",
        schema="FINFLOW_SCHEMA"
    )

    print(f"Accounts loaded: {nrows}")

else:
    print("No new accounts to load.")


# Incrementally load transactions table to Snowflake

with engine.connect() as pg_conn:
    transactions_df = pd.read_sql(
        transaction_query,
        con=pg_conn,
        params={"last_loaded_id": accts_last_loaded_id}
    )

if not transactions_df.empty:
    transactions_df.columns = transactions_df.columns.str.upper()

    success, nchunks, nrows, output = write_pandas(
        conn=sf_conn,
        df=transactions_df,
        table_name="TRANSACTIONS",
        schema="FINFLOW_SCHEMA"
    )

    print(f"Transactions loaded: {nrows}")

else:
    print("No new accounts to load.")