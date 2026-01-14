# ⚙️ Configuration Guide

## Environment Variables

This project uses environment variables for configuration. Create a `.env` file in the project root with the following variables:

### Required Variables

```bash
# MinIO Configuration (Data Lake)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123

# PostgreSQL Configuration (Data Warehouse)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_DB=cnpj_analytics
```

### Variable Descriptions

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MINIO_ROOT_USER` | MinIO admin username | `minioadmin` | Yes |
| `MINIO_ROOT_PASSWORD` | MinIO admin password | `minioadmin123` | Yes |
| `POSTGRES_USER` | PostgreSQL username | `postgres` | Yes |
| `POSTGRES_PASSWORD` | PostgreSQL password | `postgres123` | Yes |
| `POSTGRES_DB` | PostgreSQL database name | `cnpj_analytics` | Yes |

### Setup Instructions

1. **Create the `.env` file:**
   ```bash
   touch .env
   ```

2. **Add the required variables:**
   ```bash
   # Copy and paste the variables above, or use:
   cat > .env << EOF
   MINIO_ROOT_USER=minioadmin
   MINIO_ROOT_PASSWORD=minioadmin123
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres123
   POSTGRES_DB=cnpj_analytics
   EOF
   ```

3. **Verify the file was created:**
   ```bash
   cat .env
   ```

### Security Best Practices

- ✅ **DO:** Use strong, unique passwords in production
- ✅ **DO:** Add `.env` to `.gitignore` (already included)
- ✅ **DO:** Use secrets management tools in production (AWS Secrets Manager, HashiCorp Vault)
- ❌ **DON'T:** Commit `.env` files to version control
- ❌ **DON'T:** Share credentials in plain text
- ❌ **DON'T:** Use default passwords in production

### Production Configuration

For production deployments, consider:

1. **Environment-specific files:**
   - `.env.development`
   - `.env.staging`
   - `.env.production`

2. **Secrets Management:**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Kubernetes Secrets
   - Docker Secrets

3. **Password Requirements:**
   - Minimum 16 characters
   - Mix of uppercase, lowercase, numbers, and symbols
   - Rotate credentials regularly (every 90 days)

### Troubleshooting

**Issue:** Scripts can't find environment variables
- **Solution:** Ensure `.env` file is in the project root directory
- **Solution:** Verify `python-dotenv` is installed: `pip install python-dotenv`

**Issue:** Docker containers can't access environment variables
- **Solution:** Check `docker-compose.yml` has the correct variable names
- **Solution:** Restart containers after changing `.env`: `docker-compose down && docker-compose up -d`

**Issue:** Connection errors to MinIO or PostgreSQL
- **Solution:** Verify credentials match in `.env` and `docker-compose.yml`
- **Solution:** Check containers are running: `docker-compose ps`
