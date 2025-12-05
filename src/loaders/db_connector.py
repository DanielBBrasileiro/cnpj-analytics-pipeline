import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_db_engine():
    """
    Creates and returns the SQLAlchemy database engine for Postgres.
    Uses .env variables for security.
    """
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = "localhost"  # Since the script runs outside Docker, access is via localhost
    port = "5432"
    db = os.getenv("POSTGRES_DB")

    # Connection string format: postgresql://user:password@host:port/dbname
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

    engine = create_engine(url)
    return engine

def test_connection():
    """Quick test to verify database accessibility"""
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            print("Connection to Postgres successful!")
    except Exception as e:
        print(f"Error connecting to the database: {e}")

if __name__ == "__main__":
    test_connection()
