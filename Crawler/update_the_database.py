import pandas as pd
from sqlalchemy import create_engine

# New database connection string
new_conn_str = 'postgresql://stock_data_i36c_user:YLMLHhfjF7oIdi3SMzexVaobFuaL37Dc@dpg-csro9ppu0jms73e1epb0-a.singapore-postgres.render.com/stock_data_i36c'
new_engine = create_engine(new_conn_str)

# Function to create a table based on the DataFrame schema
def create_table_from_df(table_name, df, engine):
    try:
        # Use pandas to create a table based on the dataframe schema
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"Table {table_name} has been created/updated.")
    except Exception as e:
        print(f"Error creating table {table_name}: {e}")

# Function to update the table with data from CSV
def update_table_from_csv(table_name, csv_file, engine):
    try:
        # Load data from CSV
        df = pd.read_csv(csv_file)
        
        # Create or update the table based on the DataFrame
        create_table_from_df(table_name, df, engine)
    except Exception as e:
        print(f"Error updating table {table_name} with data from {csv_file}: {e}")

# csv_files = ["stock_data.csv", "stock_index.csv", "stock_info.csv", "article.csv", "financial_metrics.csv"]
# table_names = ["stock_data", "stock_index", "stock_info", "article", "financial_metrics"] 

csv_files = ["stock_data.csv"]
table_names = ["stock_data"]

for csv_file, table_name in zip(csv_files, table_names):
    update_table_from_csv(table_name, csv_file, new_engine)

