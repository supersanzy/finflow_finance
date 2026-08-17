from data_generator.db_connection import connect_and_validate_db
from data_ingestion.snowflake_python import sf_connect

import pandas as pd

from sqlalchemy import text
from snowflake.connector.pandas_tools import write_pandas


# ============================================================
# CONNECTIONS
# ============================================================

engine = connect_and_validate_db()
sf_conn = sf_connect()

schema = "FINFLOW_SCHEMA"


# ============================================================
# GET LAST LOADED ID FROM SNOWFLAKE
# ============================================================

def get_last_loaded_id(conn, table_name, id_column):

    cursor = conn.cursor()

    query = f"""
        SELECT MAX({id_column})
        FROM {schema}.{table_name}
    """

    cursor.execute(query)

    last_loaded_id = cursor.fetchone()[0]

    return (
        last_loaded_id
        if last_loaded_id is not None
        else 0
    )


# ============================================================
# GET WATERMARKS
# ============================================================

customers_last_loaded_id = get_last_loaded_id(
    sf_conn,
    "CUSTOMERS",
    "CUSTOMER_ID"
)


accounts_last_loaded_id = get_last_loaded_id(
    sf_conn,
    "ACCOUNTS",
    "ACCOUNT_ID"
)


transactions_last_loaded_id = get_last_loaded_id(
    sf_conn,
    "TRANSACTIONS",
    "TRANSACTION_ID"
)


print(f"Last customer ID loaded: {customers_last_loaded_id}")

print(f"Last account ID loaded: {accounts_last_loaded_id}")

print(
    f"Last transaction ID loaded: "
    f"{transactions_last_loaded_id}"
)


# ============================================================
# POSTGRES QUERIES
# ============================================================

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


# ============================================================
# FORMAT DATETIME COLUMNS
# ============================================================

def format_datetime_columns(df):

    for col in df.columns:

        if pd.api.types.is_datetime64_any_dtype(df[col]):

            df[col] = df[col].dt.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

    return df


# ============================================================
# LOAD CUSTOMERS
# ============================================================

print("\nLoading customers...")


with engine.connect() as pg_conn:

    customers_df = pd.read_sql(
        customer_query,
        con=pg_conn,
        params={
            "last_loaded_id": customers_last_loaded_id
        }
    )


if not customers_df.empty:

    customers_df = format_datetime_columns(
        customers_df
    )

    customers_df.columns = (
        customers_df.columns.str.upper()
    )

    success, nchunks, nrows, output = write_pandas(
        conn=sf_conn,
        df=customers_df,
        table_name="CUSTOMERS",
        schema=schema
    )

    print(f"Customers loaded: {nrows}")

else:

    print("No new customers to load.")


# ============================================================
# LOAD ACCOUNTS
# ============================================================

print("\nLoading accounts...")


with engine.connect() as pg_conn:

    accounts_df = pd.read_sql(
        account_query,
        con=pg_conn,
        params={
            "last_loaded_id": accounts_last_loaded_id
        }
    )


if not accounts_df.empty:

    accounts_df = format_datetime_columns(
        accounts_df
    )

    accounts_df.columns = (
        accounts_df.columns.str.upper()
    )

    success, nchunks, nrows, output = write_pandas(
        conn=sf_conn,
        df=accounts_df,
        table_name="ACCOUNTS",
        schema=schema
    )

    print(f"Accounts loaded: {nrows}")

else:

    print("No new accounts to load.")


# ============================================================
# LOAD TRANSACTIONS
# ============================================================

print("\nLoading transactions...")


with engine.connect() as pg_conn:

    transactions_df = pd.read_sql(
        transaction_query,
        con=pg_conn,
        params={
            "last_loaded_id": transactions_last_loaded_id
        }
    )


if not transactions_df.empty:

    transactions_df = format_datetime_columns(
        transactions_df
    )

    transactions_df.columns = (
        transactions_df.columns.str.upper()
    )

    success, nchunks, nrows, output = write_pandas(
        conn=sf_conn,
        df=transactions_df,
        table_name="TRANSACTIONS",
        schema=schema
    )

    print(f"Transactions loaded: {nrows}")

else:

    print("No new transactions to load.")


# ============================================================
# CLOSE SNOWFLAKE CONNECTION
# ============================================================

sf_conn.close()

print("\nIncremental ingestion completed successfully.")