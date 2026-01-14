# CNPJ Analytics & Compliance Pipeline

## 📋 Overview

An end-to-end data engineering project that ingests Brazilian public company data from the Federal Revenue Service (Receita Federal), processes it using a modern data lakehouse architecture, and provides analytics insights through a Data Warehouse.

This pipeline implements a **Bronze-Silver-Gold** data architecture pattern, transforming raw government data into structured, queryable information suitable for business intelligence and compliance analysis.

## 🏗️ Architecture

- **Bronze Layer (Raw):** Python extractors with MinIO (S3-compatible object storage)
- **Silver Layer (Cleaned):** Pandas transformations to Parquet format
- **Gold Layer (Curated):** PostgreSQL Data Warehouse with optimized schemas
- **Visualization:** Streamlit dashboard for data exploration
- **Infrastructure:** Docker Compose for containerized services

For detailed architectural decisions, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Python 3.10+** (for running pipeline scripts)
- **Git** (for cloning the repository)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd cnpj-analytics-pipeline
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the project root. See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for detailed instructions.
   
   Quick setup:
   ```bash
   # MinIO Configuration
   MINIO_ROOT_USER=minioadmin
   MINIO_ROOT_PASSWORD=minioadmin123

   # PostgreSQL Configuration
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres123
   POSTGRES_DB=cnpj_analytics
   ```

5. **Start infrastructure services:**
   ```bash
   docker-compose up -d
   ```

   This will start:
   - **MinIO** on `http://localhost:9000` (API) and `http://localhost:9001` (Console)
   - **PostgreSQL** on `localhost:5432`

6. **Verify services are running:**
   ```bash
   docker-compose ps
   ```

### Running the Pipeline

#### Option 1: Generate Mock Data (Recommended for Testing)

First, generate sample data that mimics the Receita Federal format:

```bash
python generate_mock_data.py
```

This creates a mock `Cnaes.zip` file in `data/raw/` that you can use to test the pipeline without downloading from the government API.

#### Option 2: Run Full Pipeline

Execute the complete data pipeline:

```bash
python run_pipeline.py
```

This will:
1. **Bronze Ingestion:** Download or use local CNAE data and upload to MinIO
2. **Silver Transformation:** Convert CSV to optimized Parquet format
3. **Gold Load:** Load data into PostgreSQL Data Warehouse
4. **Optimization:** Create indexes and constraints for performance

#### Option 3: Run Individual Steps

You can also run each step independently:

```bash
# Bronze layer (ingestion)
python src/extractors/ingest_bronze.py

# Silver layer (transformation)
python src/transformers/process_cnaes.py

# Gold layer (database load)
python src/loaders/load_cnaes_gold.py

# Database optimization
python src/loaders/optimize_gold.py
```

### Accessing Services

- **MinIO Console:** http://localhost:9001
  - Login with credentials from `.env` file
  - Browse buckets: `raw-data` (Bronze) and `silver-data` (Silver)

- **PostgreSQL:**
  ```bash
  psql -h localhost -U postgres -d cnpj_analytics
  ```

- **Streamlit Dashboard:**
  ```bash
  cd src/visualization
  streamlit run app.py
  ```
  Then open http://localhost:8501 in your browser

## 📁 Project Structure

```
cnpj-analytics-pipeline/
├── data/
│   ├── raw/              # Raw data files (Bronze layer source)
│   └── processed/        # Local Parquet files (temporary)
├── docs/
│   └── ARCHITECTURE.md   # Detailed architecture documentation
├── src/
│   ├── extractors/       # Bronze layer: Data ingestion
│   │   └── ingest_bronze.py
│   ├── transformers/     # Silver layer: Data transformation
│   │   └── process_cnaes.py
│   ├── loaders/          # Gold layer: Database loading
│   │   ├── db_connector.py
│   │   ├── load_cnaes_gold.py
│   │   └── optimize_gold.py
│   └── visualization/    # Streamlit dashboard
│       ├── app.py
│       └── queries.py
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docker-compose.yml    # Infrastructure services
├── Dockerfile            # Application container (if needed)
├── requirements.txt      # Python dependencies
├── run_pipeline.py       # Main pipeline orchestrator
└── generate_mock_data.py # Mock data generator for testing
```

## 🔄 Data Flow

```
Receita Federal API
        ↓
[Bronze Layer] → MinIO (raw-data bucket) → Raw .zip files
        ↓
[Silver Layer] → MinIO (silver-data bucket) → Parquet files
        ↓
[Gold Layer] → PostgreSQL → dim_cnaes table
        ↓
[Visualization] → Streamlit Dashboard
```

## 📊 Current Data Sources

### CNAE (National Classification of Economic Activities)
- **Source:** http://dadosabertos.rfb.gov.br/CNPJ/Cnaes.zip
- **Format:** CSV (semicolon-separated, Latin-1 encoding, no headers)
- **Schema:**
  - `codigo_cnae` (String): 7-digit activity code
  - `descricao_cnae` (String): Activity description

## 🛠️ Development

### Adding New Data Sources

1. Create a new extractor in `src/extractors/`
2. Add transformation logic in `src/transformers/`
3. Create loader in `src/loaders/`
4. Update `run_pipeline.py` to include the new steps

### Testing

```bash
# Run unit tests (when implemented)
pytest tests/unit/

# Run integration tests (when implemented)
pytest tests/integration/
```

### Code Quality

```bash
# Format code (if using black)
black src/

# Lint code (if using pylint)
pylint src/
```

## 🐛 Troubleshooting

### MinIO Connection Issues
- Verify Docker containers are running: `docker-compose ps`
- Check MinIO credentials in `.env` file
- Ensure MinIO is accessible at `http://localhost:9000`

### PostgreSQL Connection Issues
- Verify PostgreSQL container is running
- Check connection credentials in `.env`
- Ensure port 5432 is not in use by another service

### Download Failures
- The Receita Federal API may be unstable or block automated requests
- Use `generate_mock_data.py` to create test data locally
- The pipeline automatically falls back to local files if download fails

### Memory Issues with Large Files
- The pipeline uses chunked processing for large files
- Consider increasing Docker memory limits if processing very large datasets

## 📝 Environment Variables

For detailed configuration instructions, see [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

| Variable | Description | Default |
|----------|-------------|---------|
| `MINIO_ROOT_USER` | MinIO admin username | `minioadmin` |
| `MINIO_ROOT_PASSWORD` | MinIO admin password | `minioadmin123` |
| `POSTGRES_USER` | PostgreSQL username | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `postgres123` |
| `POSTGRES_DB` | PostgreSQL database name | `cnpj_analytics` |

## 🔮 Roadmap

- [ ] Add more data sources (Companies, Partners, etc.)
- [ ] Implement data quality checks (Pydantic/Great Expectations)
- [ ] Add orchestration (Airflow/Dagster)
- [ ] Implement incremental loading strategies
- [ ] Add comprehensive test coverage
- [ ] Set up CI/CD pipeline
- [ ] Add monitoring and alerting
- [ ] Expand visualization capabilities

## 📄 License

[Add your license here]

## 👥 Contributing

[Add contribution guidelines here]

## 📧 Contact

[Add contact information here]
