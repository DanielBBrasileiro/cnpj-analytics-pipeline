import subprocess
import time
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("CNPJ_Pipeline")

def run_step(script_path, step_name):
    """
    Executes a Python script as a subprocess and monitors errors.
    """
    logger.info(f"Starting step: {step_name}...")
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ["python", script_path],
            check=True,
            capture_output=True,
            text=True
        )
        
        elapsed = time.time() - start_time
        logger.info(f"Step '{step_name}' completed in {elapsed:.2f}s")

    except subprocess.CalledProcessError as e:
        logger.error(f"Step '{step_name}' failed.")
        logger.error(f"Error: {e.stderr}")
        raise e

def main():
    logger.info("==========================================")
    logger.info("STARTING CNPJ DATA PIPELINE")
    logger.info("==========================================")
    
    total_start = time.time()

    try:
        # 1. Bronze Layer (Ingestion)
        run_step("src/extractors/ingest_bronze.py", "Bronze Ingestion (MinIO)")

        # 2. Silver Layer (Transformation)
        run_step("src/transformers/process_cnaes.py", "Silver Transformation (Parquet)")

        # 3. Gold Layer (Database Load)
        run_step("src/loaders/load_cnaes_gold.py", "Gold Load (Postgres)")

        # 4. Optimization (Indexes, Constraints)
        run_step("src/loaders/optimize_gold.py", "Database Optimization (DDL)")

        total_time = time.time() - total_start
        logger.info("==========================================")
        logger.info(f"PIPELINE FINISHED SUCCESSFULLY IN {total_time:.2f}s")
        logger.info("==========================================")

    except Exception:
        logger.critical("Pipeline was stopped due to errors.")

if __name__ == "__main__":
    main()

