from sqlalchemy import create_engine, Column, String, Date, PrimaryKeyConstraint, Table, MetaData

# Connect to PostgreSQL
engine = create_engine('postgresql+psycopg2://caokhoi:m6ikFt3TKwnkV75fNZ2FBdKiEHKEu1sN@dpg-cs87v7m8ii6s73c5m19g-a.singapore-postgres.render.com:5432/stock_data_01')

create_article_table_query = """
CREATE TABLE IF NOT EXISTS article (
    title VARCHAR(255),
    link TEXT,
    content TEXT,
    date DATE,
    PRIMARY KEY (title, date)  -- Composite primary key
);
"""

# Execute the query to create the table
with engine.connect() as connection:
    connection.execute(create_article_table_query)

print("Table 'article' created successfully.")

