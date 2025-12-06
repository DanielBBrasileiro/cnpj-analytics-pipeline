import sys
import os
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.loaders.db_connector import get_db_engine

def optimize_tables():
    engine = get_db_engine()

    print("Optimizing Gold tables...")

    # Raw SQL to adjust the table:
    # 1. Set 'codigo_cnae' as NOT NULL
    # 2. Add PRIMARY KEY on 'codigo_cnae'
    # 3. Add a COMMENT to the table
    sql_commands = [
        """
        ALTER TABLE dim_cnaes 
        ALTER COLUMN codigo_cnae SET NOT NULL;
        """,
        """
        ALTER TABLE dim_cnaes 
        ADD PRIMARY KEY (codigo_cnae);
        """,
        """
        COMMENT ON TABLE dim_cnaes IS 'Dimension Table: Brazilian National Classification of Economic Activities';
        """
    ]

    with engine.connect() as conn:
        for sql in sql_commands:
            try:
                conn.execute(text(sql))
                conn.commit()  # Important: commit the change
                print(f"Executed: {sql.strip().splitlines()[0]}...")
            except Exception as e:
                print(f"Warning (may already exist): {e}")

    print("Optimization complete.")

if __name__ == "__main__":
    optimize_tables()

