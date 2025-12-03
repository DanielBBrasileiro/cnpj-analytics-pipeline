# 🏗️ Architecture & Technical Decisions

## Overview
This document outlines the architectural choices and engineering principles applied to the CNPJ Analytics Pipeline. The goal is to build a scalable, reproducible, and modern **Data Lakehouse** environment using open-source technologies.

---

## 🛠️ The Tech Stack (Days 1-4)

### 1. Infrastructure as Code (Docker)
Instead of local installations, we adopted a **Containerized approach** using Docker Compose.
* **Decision:** Isolate services (MinIO, PostgreSQL) to ensure environment parity between development and production.
* **Components:**
    * `datalake-minio`: S3-compatible Object Storage for the Data Lake layers.
    * `datawarehouse-postgres`: Relational database for the serving layer.

### 2. The Bronze Layer (Raw Ingestion)
* **Pattern:** ELT (Extract, Load, Transform).
* **Challenge:** The source API (Receita Federal) is unstable and frequently blocks automated requests.
* **Solution:**
    * Implemented a resilient Python extractor (`ingest_bronze.py`) with custom `User-Agent` headers to bypass basic firewalls.
    * Added **Contingency Logic**: The pipeline checks for local files before attempting a download, allowing for manual overrides (Hybrid Ingestion) during API downtimes.
    * **Storage:** Raw `.zip` files are stored in MinIO (`raw-data` bucket) to preserve historical fidelity.

### 3. The Silver Layer (Transformation & Optimization)
* **Goal:** Convert raw, unstructured text into optimized columnar storage.
* **Tooling:** Pandas (Python).
* **Key Engineering Decisions:**
    * **Format:** Converted CSV to **Parquet** (Snappy compression).
    * **Why Parquet?** It reduced file size by ~80% compared to raw CSVs and preserves schema metadata (data types), enabling faster I/O for downstream consumption.
    * **Schema Enforcement:** Manually mapped missing headers for the `CNAE` dataset to ensure data consistency before loading.

---

## 🔮 Future Roadmap (Days 5-100)
* **Gold Layer:** Loading enriched data into PostgreSQL for SQL-based analytics.
* **Orchestration:** Implementing Airflow or Dagster to manage dependencies.
* **Data Quality:** integrating Pydantic or Great Expectations to validate data contracts.
