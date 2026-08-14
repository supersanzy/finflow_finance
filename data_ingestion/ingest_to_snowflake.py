from data_generator.db_connection import connect_and_validate_db
from data_ingestion.snowflake_python import sf_connect
import pandas as pd
from sqlalchemy import text
from snowflake.connector.pandas_tools import write_pandas

conn = sf_connect()
engine = connect_and_validate_db()
schema = 'finflow_schema'
tables = ['customers', 'accounts', 'beneficiaries', 'transactions', 'transfers', 
          'cards', 'card_transactions', 'loans', 'loan_payments']
# tables = ["customers"]
try:
    for t in tables:
        query = text(f"""
            select * from {schema}.{t}    
        """)

        df = pd.read_sql(query,con=engine)

        # Convert datetime columns to a Snowflake-safe string format
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

        df.columns = df.columns.str.upper()

        success, chunks, nrows, output = write_pandas(
            conn=conn,
            df=df,
            table_name=t.upper(),
            database='FINFLOW_DB',
            schema="FINFLOW_SCHEMA",
            quote_identifiers=False
        )

        if success:
            print(f"{t}: {nrows} rows loaded successfully.")
        
except Exception as error:
    print(f"Loading failed {error}")
