import sys
import os
import boto3
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv

# Add the project root to the Python path so we can import db_connector
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.loaders.db_connector import get_db_engine

load_dotenv()

# Configurations
MINIO_ENDPOINT = "http://localhost:9000"
ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
SILVER_BUCKET = "silver-data"
PARQUET_FILE = "cnaes.parquet"
TABLE_NAME = "dim_cnaes"  # Name of the table in the database (Dimension)

def main():
    # 1. Connect to MinIO
    print("Connecting to MinIO...")
    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )

    # 2. Read Parquet from the Silver layer
    print(f"Downloading {PARQUET_FILE} from the Silver layer...")
    try:
        obj = s3.get_object(Bucket=SILVER_BUCKET, Key=PARQUET_FILE)
        buffer = BytesIO(obj["Body"].read())
        df = pd.read_parquet(buffer)
        print(f"Rows loaded: {len(df)}")
    except Exception as e:
        print(f"Error reading from MinIO: {e}")
        return

    # 3. Connect to Postgres
    print("Connecting to the Data Warehouse (Postgres)...")
    engine = get_db_engine()

    # 4. Load the data
    print(f"Writing data to the '{TABLE_NAME}' table...")

    # if_exists='replace': Drops the old table and creates a new one (Full Load)
    # index=False: Prevents Pandas from creating an index column
    try:
        df.to_sql(TABLE_NAME, engine, if_exists='replace', index=False)
        print("Success! Gold layer load completed.")
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    main()

