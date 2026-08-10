import duckdb
from pathlib import Path

def init_duckdb():
    db_path = Path("data/telemetry_warehouse.duckdb")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = duckdb.connect(str(db_path))
    conn.execute("CREATE TABLE IF NOT EXISTS system_check (id INT, status TEXT);")
    conn.execute("INSERT INTO system_check VALUES (1, 'DuckDB Engine Online');")
    result = conn.execute("SELECT * FROM system_check;").fetchall()
    
    print(f"Database initialized successfully: {result}")
    conn.close()

if __name__ == "__main__":
    init_duckdb()