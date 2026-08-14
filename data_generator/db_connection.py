import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()


DB_PASSWORD = os.getenv('DB_PASSWORD')
DATABASE = os.getenv('DB_NAME')
USER = os.getenv('DB_USER')
PORT = os.getenv('DB_PORT')
HOST = os.getenv('DB_HOST')


def connect_and_validate_db():
    try:
        engine = create_engine(
            f'postgresql+psycopg2://{USER}:{DB_PASSWORD}@{HOST}:{PORT}/{DATABASE}'
        )

        with engine.connect() as conn:
            print("Database connection successful.")

        return engine

    except Exception as error:
        print(f"Database connection failed: {error}")
        raise

