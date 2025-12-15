import sys
import os
import pandas as pd

# Import the engine from our existing connector
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.loaders.db_connector import get_db_engine

def get_total_cnaes():
    """Returns the total count of registered economic activities."""
    engine = get_db_engine()
    query = "SELECT COUNT(*) AS total FROM dim_cnaes;"
    df = pd.read_sql(query, engine)
    return df['total'][0]

def get_cnaes_by_sector():
    """
    Groups CNAEs by the first 2 digits to simulate sectors.
    Example: 62xxxx (IT), 01xxxx (Agriculture).
    """
    engine = get_db_engine()
    # Extract the first 2 digits of the code as 'sector'
    query = """
    SELECT 
        SUBSTRING(codigo_cnae, 1, 2) AS sector,
        COUNT(*) AS quantity
    FROM dim_cnaes
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 10;
    """
    return pd.read_sql(query, engine)

def search_cnae(keyword):
    """Searches CNAEs by keyword in the description."""
    engine = get_db_engine()
    # Basic sanitization to avoid simple SQL injection
    safe_keyword = keyword.replace("'", "")
    
    query = f"""
    SELECT codigo_cnae, descricao_cnae
    FROM dim_cnaes
    WHERE descricao_cnae ILIKE '%%{safe_keyword}%%'
    LIMIT 20;
    """
    return pd.read_sql(query, engine)

