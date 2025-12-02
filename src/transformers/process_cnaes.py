import os
import boto3
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# Configurations
MINIO_ENDPOINT = "http://localhost:9000"
ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")

# Buckets
BRONZE_BUCKET = "raw-data"
SILVER_BUCKET = "silver-data"  # New bucket for cleaned data

# Files
FILENAME = "Cnaes.zip"
CSV_FILENAME_INSIDE_ZIP = "Cnaes.csv"  # Receita usually names it like this inside the zip
PARQUET_FILENAME = "cnaes.parquet"

def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )

def main():
    s3_client = get_minio_client()

    # 1. Ensure the Silver bucket exists
    try:
        s3_client.head_bucket(Bucket=SILVER_BUCKET)
    except:
        print(f"Creating bucket '{SILVER_BUCKET}'...")
        s3_client.create_bucket(Bucket=SILVER_BUCKET)

    print("Reading data from the Bronze layer (MinIO)...")
    
    # Engineering trick: read directly from memory without saving to disk
    try:
        obj = s3_client.get_object(Bucket=BRONZE_BUCKET, Key=FILENAME)
        buffer = BytesIO(obj["Body"].read())
    except Exception as e:
        print(f"Error reading from MinIO. Does the file {FILENAME} exist there?")
        print(e)
        return

    print("Transforming with Pandas...")
    
    # The Receita data DOES NOT have a header, uses ';' as separator, and 'latin-1' encoding
    try:
        df = pd.read_csv(
            buffer,
            compression='zip',
            sep=';',
            encoding='latin-1',
            header=None,  # Important: real file does not have header
            names=['codigo_cnae', 'descricao_cnae'],  # We define the schema
            dtype=str  # Forces all fields as text to avoid losing leading zeros
        )
        
        print(f"- Rows processed: {len(df)}")
        print(f"- Example: {df.iloc[0].values}")

    except Exception as e:
        print("Error processing CSV. If you're using yesterday's FAKE file, the format is different.")
        print(e)
        return

    # Save to Parquet locally (temporary)
    local_parquet = f"data/processed/{PARQUET_FILENAME}"
    os.makedirs(os.path.dirname(local_parquet), exist_ok=True)
    
    df.to_parquet(local_parquet, index=False, compression='snappy')
    print(f"Converted to Parquet: {local_parquet}")

    # Upload to Silver
    print("Uploading to the Silver layer")
    s3_client.upload_file(local_parquet, SILVER_BUCKET, PARQUET_FILENAME)
    
    print(f"Success! Available at: s3://{SILVER_BUCKET}/{PARQUET_FILENAME}")


if __name__ == "__main__":
    main()

