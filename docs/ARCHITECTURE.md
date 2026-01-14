# 🏗️ Architecture & Technical Decisions

## Overview

This document outlines the architectural choices and engineering principles applied to the CNPJ Analytics Pipeline. The goal is to build a scalable, reproducible, and modern **Data Lakehouse** environment using open-source technologies.

The pipeline follows the **Medallion Architecture** pattern (Bronze-Silver-Gold), which provides clear separation of concerns and enables incremental data quality improvements as data flows through the system.

---

## 🏛️ System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Data Sources                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Receita Federal API (dadosabertos.rfb.gov.br)          │   │
│  │  - CNAE files (.zip)                                     │   │
│  │  - Company data (future)                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BRONZE LAYER (Raw)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Python Extractor (ingest_bronze.py)                     │   │
│  │  - Resilient download with retry logic                   │   │
│  │  - User-Agent headers for bypass                         │   │
│  │  - Local file fallback (contingency mode)                │   │
│  └──────────────────────────┬───────────────────────────────┘   │
│                             │                                    │
│  ┌──────────────────────────▼───────────────────────────────┐   │
│  │  MinIO (S3-Compatible)                                    │   │
│  │  Bucket: raw-data                                         │   │
│  │  Format: .zip (preserves original format)                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SILVER LAYER (Cleaned)                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Pandas Transformer (process_cnaes.py)                    │   │
│  │  - CSV parsing (semicolon, latin-1, no headers)          │   │
│  │  - Schema enforcement                                     │   │
│  │  - Data type normalization                                │   │
│  └──────────────────────────┬───────────────────────────────┘   │
│                             │                                    │
│  ┌──────────────────────────▼───────────────────────────────┐   │
│  │  MinIO (S3-Compatible)                                    │   │
│  │  Bucket: silver-data                                      │   │
│  │  Format: Parquet (Snappy compression)                     │   │
│  │  Benefits: ~80% size reduction, schema preservation       │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GOLD LAYER (Curated)                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PostgreSQL Loader (load_cnaes_gold.py)                  │   │
│  │  - Full load strategy (replace)                           │   │
│  │  - Dimension table: dim_cnaes                            │   │
│  └──────────────────────────┬───────────────────────────────┘   │
│                             │                                    │
│  ┌──────────────────────────▼───────────────────────────────┐   │
│  │  PostgreSQL Data Warehouse                               │   │
│  │  - Optimized schemas (optimize_gold.py)                  │   │
│  │  - Primary keys, constraints, indexes                    │   │
│  │  - Ready for SQL analytics                               │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VISUALIZATION LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Streamlit Dashboard (app.py)                            │   │
│  │  - Interactive queries (queries.py)                      │   │
│  │  - Plotly visualizations                                  │   │
│  │  - Real-time analytics                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Infrastructure Layer

#### Docker & Docker Compose
**Decision:** Containerized infrastructure for environment consistency.

**Rationale:**
- Ensures identical environments across development, staging, and production
- Simplifies dependency management
- Enables easy scaling and deployment
- Isolates services to prevent conflicts

**Components:**
- `datalake-minio`: S3-compatible object storage (ports 9000, 9001)
- `datawarehouse-postgres`: PostgreSQL 15 (port 5432)
- Shared network: `pipeline-network` (bridge driver)
- Persistent volumes for data durability

#### MinIO (Object Storage)
**Decision:** Use MinIO as S3-compatible storage instead of AWS S3.

**Rationale:**
- Zero cost for local development
- Full S3 API compatibility (easy migration to AWS if needed)
- Self-hosted solution (data sovereignty)
- Web UI for easy file browsing

**Configuration:**
- Endpoint: `http://localhost:9000` (API)
- Console: `http://localhost:9001` (Web UI)
- Buckets: `raw-data` (Bronze), `silver-data` (Silver)

#### PostgreSQL (Data Warehouse)
**Decision:** Use PostgreSQL as the serving layer for analytics.

**Rationale:**
- Mature, battle-tested relational database
- Excellent SQL support for complex analytics
- Strong ecosystem (BI tools, ORMs, etc.)
- ACID compliance for data integrity
- Extensible with extensions (PostGIS, etc.)

**Configuration:**
- Version: PostgreSQL 15 (Alpine Linux base)
- Port: 5432
- Database: `cnpj_analytics`

---

## 📊 Data Layers

### Bronze Layer (Raw Ingestion)

**Purpose:** Preserve raw data exactly as received from source systems.

**Pattern:** ELT (Extract, Load, Transform) - Load first, transform later.

**Key Characteristics:**
- **Immutable:** Raw data is never modified
- **Historical Fidelity:** Preserves original format and encoding
- **Schema-on-Read:** No schema enforcement at this layer
- **Storage:** Original `.zip` files from Receita Federal

**Implementation Details:**

1. **Resilient Download (`ingest_bronze.py`):**
   - Custom `User-Agent` headers to bypass basic firewalls
   - SSL verification disabled (government certificates may be invalid)
   - Chunked streaming download (prevents memory issues)
   - 60-second timeout for slow connections

2. **Contingency Logic:**
   - Checks for local files before attempting download
   - Enables "Hybrid Ingestion" mode during API downtimes
   - Allows manual file placement for testing

3. **Storage Strategy:**
   - Files stored in MinIO `raw-data` bucket
   - Original filenames preserved
   - No transformation or processing applied

**Challenges Addressed:**
- Receita Federal API instability
- Automated request blocking
- SSL certificate issues
- Network timeouts

---

### Silver Layer (Transformation & Optimization)

**Purpose:** Clean, validate, and optimize data for downstream consumption.

**Key Characteristics:**
- **Schema Enforcement:** Explicit column names and data types
- **Format Optimization:** Columnar storage (Parquet)
- **Data Quality:** Basic validation and normalization
- **Storage:** Optimized Parquet files with Snappy compression

**Implementation Details:**

1. **CSV Parsing (`process_cnaes.py`):**
   - **Separator:** Semicolon (`;`) - Receita Federal standard
   - **Encoding:** Latin-1 (ISO-8859-1) - Brazilian Portuguese support
   - **Headers:** None (manually defined schema)
   - **Data Types:** String (preserves leading zeros in codes)

2. **Schema Definition:**
   ```python
   names=['codigo_cnae', 'descricao_cnae']
   dtype=str  # Prevents type coercion that could lose leading zeros
   ```

3. **Parquet Conversion:**
   - **Compression:** Snappy (good balance of speed and size)
   - **Benefits:**
     - ~80% size reduction vs. CSV
     - Schema metadata preservation
     - Columnar storage (faster column scans)
     - Type safety (no parsing errors downstream)

4. **Storage Strategy:**
   - Files stored in MinIO `silver-data` bucket
   - Naming convention: `{dataset}.parquet` (e.g., `cnaes.parquet`)
   - Temporary local storage during processing (cleaned up)

**Performance Considerations:**
- In-memory processing with Pandas (suitable for datasets < RAM)
- For larger datasets, consider Dask or Spark
- Streaming processing possible with `chunksize` parameter

---

### Gold Layer (Curated Data Warehouse)

**Purpose:** Serve business-ready data for analytics and reporting.

**Key Characteristics:**
- **Dimensional Modeling:** Star schema approach (dimension tables)
- **Optimized for Query:** Indexes, constraints, primary keys
- **Data Quality:** NOT NULL constraints, referential integrity
- **Storage:** PostgreSQL relational database

**Implementation Details:**

1. **Table Design (`load_cnaes_gold.py`):**
   - **Table Name:** `dim_cnaes` (dimension table)
   - **Load Strategy:** Full load with `if_exists='replace'`
   - **Schema:**
     ```sql
     CREATE TABLE dim_cnaes (
         codigo_cnae VARCHAR(7) PRIMARY KEY,
         descricao_cnae TEXT
     );
     ```

2. **Optimization (`optimize_gold.py`):**
   - **Primary Key:** `codigo_cnae` (unique identifier)
   - **NOT NULL Constraints:** Ensures data quality
   - **Table Comments:** Documentation for data governance
   - **Future:** Indexes on frequently queried columns

3. **Load Strategy:**
   - **Current:** Full replace (suitable for small, slowly-changing dimensions)
   - **Future:** Incremental loads (SCD Type 2) for larger datasets
   - **Future:** Partitioning for time-series data

**Query Performance:**
- Primary key enables fast lookups
- Indexes on foreign keys (when fact tables are added)
- Materialized views for common aggregations (future)

---

## 🔄 Data Flow & Processing

### Pipeline Execution Flow

```
1. BRONZE INGESTION
   ├─ Check local file existence
   ├─ If not found: Download from Receita Federal API
   ├─ Upload to MinIO (raw-data bucket)
   └─ Log success/failure

2. SILVER TRANSFORMATION
   ├─ Download .zip from MinIO
   ├─ Extract and parse CSV
   ├─ Apply schema and data types
   ├─ Convert to Parquet
   └─ Upload to MinIO (silver-data bucket)

3. GOLD LOAD
   ├─ Download Parquet from MinIO
   ├─ Connect to PostgreSQL
   ├─ Load into dim_cnaes table
   └─ Log row count

4. OPTIMIZATION
   ├─ Add primary key constraint
   ├─ Add NOT NULL constraints
   ├─ Add table comments
   └─ Verify constraints
```

### Error Handling Strategy

- **Bronze Layer:** Falls back to local files if download fails
- **Silver Layer:** Validates data format before processing
- **Gold Layer:** Transaction-based loading (all-or-nothing)
- **Logging:** Structured logging at each step for debugging

---

## 📐 Data Models

### Current Schema: CNAE Dimension

```sql
-- Dimension Table: CNAE (National Classification of Economic Activities)
CREATE TABLE dim_cnaes (
    codigo_cnae VARCHAR(7) PRIMARY KEY NOT NULL,
    descricao_cnae TEXT NOT NULL
);

COMMENT ON TABLE dim_cnaes IS 
    'Dimension Table: Brazilian National Classification of Economic Activities';
```

**Data Characteristics:**
- **codigo_cnae:** 7-digit code (e.g., "0111301")
- **descricao_cnae:** Activity description in Portuguese
- **Cardinality:** ~1,600+ unique activities
- **Update Frequency:** Low (quarterly updates from Receita Federal)

### Future Schema Extensions

**Fact Tables (Planned):**
- `fct_empresas`: Company registrations
- `fct_socios`: Company partners/owners
- `fct_estabelecimentos`: Business establishments

**Additional Dimensions:**
- `dim_municipios`: Brazilian municipalities
- `dim_uf`: Brazilian states
- `dim_natureza_juridica`: Legal entity types

---

## 🎯 Design Principles

### 1. Separation of Concerns
Each layer has a single, well-defined responsibility:
- **Bronze:** Raw data preservation
- **Silver:** Data cleaning and optimization
- **Gold:** Business-ready analytics

### 2. Idempotency
Pipeline steps can be safely re-run:
- Bronze: Checks for existing files
- Silver: Overwrites Parquet files
- Gold: Replaces table contents

### 3. Fail-Safe Defaults
- Local file fallback for downloads
- Error logging at each step
- Transaction-based database operations

### 4. Scalability Considerations
- **Current:** Suitable for datasets < 10GB
- **Future:** Spark/Dask for larger datasets
- **Future:** Partitioning strategies for time-series data
- **Future:** Incremental loading for efficiency

---

## 🔮 Future Roadmap

### Short Term (Days 5-30)
- [ ] **Data Quality Framework:**
  - Integrate Pydantic for schema validation
  - Add Great Expectations for data quality checks
  - Implement data profiling and anomaly detection

- [ ] **Additional Data Sources:**
  - Company data (Empresas)
  - Partner data (Sócios)
  - Establishment data (Estabelecimentos)

- [ ] **Incremental Loading:**
  - Implement SCD Type 2 for slowly changing dimensions
  - Add change data capture (CDC) logic
  - Optimize for large datasets

### Medium Term (Days 31-60)
- [ ] **Orchestration:**
  - Implement Airflow or Dagster
  - Define DAGs for pipeline dependencies
  - Add scheduling and monitoring

- [ ] **Performance Optimization:**
  - Add partitioning to fact tables
  - Create materialized views for common queries
  - Implement query result caching

- [ ] **Testing:**
  - Unit tests for each component
  - Integration tests for full pipeline
  - Data quality test suite

### Long Term (Days 61-100)
- [ ] **Advanced Analytics:**
  - Machine learning models for compliance prediction
  - Anomaly detection for suspicious patterns
  - Trend analysis and forecasting

- [ ] **Data Governance:**
  - Data lineage tracking
  - Access control and security
  - Audit logging

- [ ] **Production Readiness:**
  - CI/CD pipeline
  - Monitoring and alerting (Prometheus, Grafana)
  - Disaster recovery procedures
  - Documentation and runbooks

---

## 📚 References

- [Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture)
- [MinIO Documentation](https://min.io/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Apache Parquet Format](https://parquet.apache.org/)
- [Receita Federal Open Data](http://dadosabertos.rfb.gov.br/)

---

## 🤝 Contributing to Architecture

When making architectural decisions, consider:
1. **Scalability:** Will this scale to 10x, 100x current size?
2. **Maintainability:** Is this easy to understand and modify?
3. **Cost:** What are the infrastructure and operational costs?
4. **Performance:** Does this meet SLA requirements?
5. **Reliability:** How does this handle failures?

Document all significant architectural decisions in this file.
