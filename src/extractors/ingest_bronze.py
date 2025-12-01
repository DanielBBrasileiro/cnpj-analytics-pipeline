import os
import requests
import boto3
from botocore.client import Config
from dotenv import load_dotenv
# Adicione essa importação no topo do arquivo se não tiver
import urllib3

# Desabilita o aviso chato de SSL inseguro
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_file(url, save_path):
    """
    Baixa o arquivo simulando um navegador real e ignorando SSL.
    """
    print(f"⬇️  Iniciando download de: {url}")
    
    # Cabeçalhos para fingir ser um navegador (Bypass em bloqueios simples)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # verify=False ignora erros de certificado SSL do governo
        # timeout=60 espera até 60 segundos antes de desistir
        response = requests.get(url, stream=True, headers=headers, verify=False, timeout=60)
        
        if response.status_code == 200:
            # --- NOVO CÓDIGO AQUI ---
            # Garante que a pasta existe. Se não existir, o Python cria (ex: data/raw)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Download concluído e salvo em: {save_path}")
            return True
        else:
            print(f"❌ Erro ao baixar arquivo. Status Code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Falha crítica no download: {e}")
        return False

load_dotenv()

# --- CONFIGURAÇÃO DE TESTE (Para destravar o dia) ---
# Vamos baixar uma lista de Pokemons em CSV. É leve, rápido e o servidor é bom.

# -----------------------------------------------------

# (Mantenha o resto do código igual, inclusive a função download_file melhorada que te passei antes)

MINIO_ENDPOINT = "http://localhost:9000"
ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
BUCKET_NAME = "raw-data"

# --- DADOS REAIS DA RECEITA FEDERAL ---
# Vamos começar com a tabela de CNAEs pois é menor (alguns MBs) e serve para validar.
# Depois baixaremos as Empresas (que são GBs).
SOURCE_URL = "http://dadosabertos.rfb.gov.br/CNPJ/Cnaes.zip"
FILENAME = "Cnaes.zip"
LOCAL_PATH = f"data/raw/{FILENAME}"

def get_minio_client():
    """
    Creates the connection client with MinIO pretending to be AWS S3.
    """
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version="s3v4"),
        verify=False
    )

def download_file(url, save_path):
    """
    Download the file in chunks so as not to overload the RAM.
    """
    print(f"Starting download from: {url}")
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Download completed and saved at: {save_path}")
        return True
    else:
        print(f"Failed to download file. Status Code: {response.status_code}")
        return False

def upload_to_datalake(client, file_path, bucket, object_name):
    """
    Upload the local file to MinIO (Data Lake).
    """
    print(f"Uploading {object_name} to MinIO...")
    try:
        client.upload_file(file_path, bucket, object_name)
        print(f"Success! File available in the Data Lake: s3://{bucket}/{object_name}")
    except Exception as e:
        print(f"Upload error: {e}")

def main():
    s3_client = get_minio_client()

    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print(f"📂 Bucket '{BUCKET_NAME}' found.")
    except:
        print(f"⚠️ Bucket '{BUCKET_NAME}' does not exist. Creating...")
        s3_client.create_bucket(Bucket=BUCKET_NAME)

    file_exists = os.path.exists(LOCAL_PATH)
    
    if file_exists:
        print(f"✅ File found locally at: {LOCAL_PATH}")
        print("⏭️  Skipping internet download (Contingency Mode).")
        upload_to_datalake(s3_client, LOCAL_PATH, BUCKET_NAME, FILENAME)
    else:
        print("File not found locally. Attempting download...")
        if download_file(SOURCE_URL, LOCAL_PATH):
            upload_to_datalake(s3_client, LOCAL_PATH, BUCKET_NAME, FILENAME)

if __name__ == "__main__":
    main()
