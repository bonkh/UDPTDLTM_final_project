import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg2://caokhoi:m6ikFt3TKwnkV75fNZ2FBdKiEHKEu1sN@dpg-cs87v7m8ii6s73c5m19g-a.singapore-postgres.render.com:5432/stock_data_01')

df = pd.read_csv('corporate_data.csv')
df_filtered = df[['CatID', 'Exchange', 'IndustryName', 'Code', 'Name', 'URL']]
df_filtered.rename(columns={
    'CatID': 'cat_id',
    'Exchange': 'exchange',
    'IndustryName': 'industry_name',
    'Code': 'code',
    'Name': 'name',
    'URL' : 'url'
}, inplace=True)

create_table_query = """
CREATE TABLE IF NOT EXISTS stock_info (
    cat_id INTEGER,
    exchange VARCHAR(50),
    industry_name VARCHAR(200),
    code VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200),
    url VARCHAR(200)
);
"""

with engine.connect() as connection:
    connection.execute(create_table_query)

with engine.connect() as connection:
    for index, row in df_filtered.iterrows():
        query = text("""
            SELECT COUNT(*) FROM stock_info 
            WHERE code = :code
        """)
        result = connection.execute(query, {'code': row['code']})
        count = result.scalar()

        if count == 0:
            row.to_frame().T.to_sql('stock_info', engine, if_exists='append', index=False)
            print(f"Inserted: {row['code']}")
        else:
            print(f"Duplicate entry for code {row['code']}, skipping.")

print("Data insertion completed.")

