from sqlalchemy import create_engine, Column, String, Date, PrimaryKeyConstraint, Table, MetaData

# Connect to PostgreSQL
engine = create_engine('postgresql://stock_data_i36c_user:YLMLHhfjF7oIdi3SMzexVaobFuaL37Dc@dpg-csro9ppu0jms73e1epb0-a.singapore-postgres.render.com/stock_data_i36c')

create_article_table_query = """
CREATE TABLE IF NOT EXISTS article (
    title VARCHAR(255),
    link TEXT,
    content TEXT,
    date DATE,
    PRIMARY KEY (title, date)
);
"""

# Execute the query to create the table
with engine.connect() as connection:
    connection.execute(create_article_table_query)

print("Table 'article' created successfully.")

