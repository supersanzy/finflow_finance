import os
import snowflake.connector as sf
from dotenv import load_dotenv

load_dotenv()


USER = os.getenv('SF_USER')
PASSWORD = os.getenv('SF_PASSWORD')
ACCOUNT = os.getenv('SF_ACCOUNT')
WAREHOUSE = os.getenv('SF_WAREHOUSE')
DATABASE = os.getenv('SF_DATABASE')
SCHEMA = os.getenv('SF_SCHEMA')

def sf_connect():
    try:
        conn = sf.connect(
            user=USER,
            password=PASSWORD,
            account=ACCOUNT,
            warehouse=WAREHOUSE,
            database=DATABASE,
            schema=SCHEMA
            )
        print("Snowflake connection successful.")

        return conn
    
    except Exception as error:
        print(f"Snowflake connection failed: {error}")
        raise

sf_connect()
