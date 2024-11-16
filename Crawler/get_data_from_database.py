import pandas as pd
from sqlalchemy import create_engine

# Database connection string (provided)
conn_str = 'postgresql+psycopg2://caokhoi:m6ikFt3TKwnkV75fNZ2FBdKiEHKEu1sN@dpg-cs87v7m8ii6s73c5m19g-a.singapore-postgres.render.com:5432/stock_data_01'
engine = create_engine(conn_str)

# Connect to the database and retrieve all table names
with engine.connect() as connection:
    # Retrieve all table names
    tables_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    result = connection.execute(tables_query)
    table_names = [row['table_name'] for row in result]

# Fetch data from each table and save to CSV
for table in table_names:
    try:
        # Read table into DataFrame
        df = pd.read_sql(f"SELECT * FROM {table}", con=engine)
        
        # Save to CSV file
        df.to_csv(f"{table}.csv", index=False)
        print(f"Data from table {table} has been saved to {table}.csv")
    
    except Exception as e:
        print(f"Error exporting table {table}: {e}")
