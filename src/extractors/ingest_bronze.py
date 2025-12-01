import os
import requests
import boto3
from botocore.client import Config
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_file(url, save_path):
    """
    Downloads the file while simulating a real browser and ignoring SSL issues.
    """
    print(f"⬇️  Starting download from: {url}")
    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        # verify=False ignores SSL certificate issues from government servers
        # timeout=60 waits up to 60 seconds before failing
        response = requests.get(url, stream=True, headers=headers, verify=False, timeout=60)
        
        if response.status_code == 200:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Download completed and saved at: {save_path}")
            return True

        else:
            print(f"Failed to download file. Status Code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Critical download failure: {e}")
        return False


load_dotenv()

MINIO_ENDPOINT = "http://localhost:9000"
ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
BUCKET_NAME = "raw-data"

SOURCE_URL = "http://dadosabertos.rfb.gov.br/CNPJ/Cnaes.zip"
FILENAME = "Cnaes.zip"
LOCAL_PATH = f"data/raw/{FILENAME}"


def get_minio_client():
    """
    Creates the MinIO client (compatible with AWS S3).
    """
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version="s3v4"),
        verify=False
    )


def upload_to_datalake(client, file_path, bucket, object_name):
    """
    Uploads the local file to MinIO (Data Lake).
    """
    print(f"Uploading {object_name} to MinIO...")

    try:
        client.upload_file(file_path, bucket, object_name)
        print(f"Success! File available at: s3://{bucket}/{object_name}")
    except Exception as e:
        print(f"Upload error: {e}")


def main():
    s3_client = get_minio_client()

    # Check/Create bucket
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' found.")
    except:
        print(f"Bucket '{BUCKET_NAME}' does not exist. Creating...")
        s3_client.create_bucket(Bucket=BUCKET_NAME)

    # Hybrid logic: use local file if available
    file_exists = os.path.exists(LOCAL_PATH)
    
    if file_exists:
        print(f"File found locally at: {LOCAL_PATH}")
        print("Skipping internet download (Contingency Mode).")
        upload_to_datalake(s3_client, LOCAL_PATH, BUCKET_NAME, FILENAME)

    else:
        print("File not found locally. Attempting download...")
        
        if download_file(SOURCE_URL, LOCAL_PATH):
            upload_to_datalake(s3_client, LOCAL_PATH, BUCKET_NAME, FILENAME)


if __name__ == "__main__":
    main()
