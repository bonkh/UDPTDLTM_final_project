import requests
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
from datetime import datetime
import os
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

engine = create_engine('postgresql+psycopg2://caokhoi:m6ikFt3TKwnkV75fNZ2FBdKiEHKEu1sN@dpg-cs87v7m8ii6s73c5m19g-a.singapore-postgres.render.com:5432/stock_data_01')
with engine.connect() as connection:
    query = text("SELECT code FROM stock_info")
    result = connection.execute(query)
    ticker_list = [row['code'] for row in result]

new_column_names = [
    'trade_date', 
    'listed_shares', 
    'shares_outstanding', 
    'reference_price', 
    'ceiling_price', 
    'floor_price', 
    'total_trading_volume', 
    'total_trading_value', 
    'market_capitalizaiton', 
    'opening_price', 
    'closing_price', 
    'highest_price', 
    'lowest_price', 
    'difference', 
    'average_price', 
    'adjusted_closing_price', 
    'price_change', 
    'price_change_percentage', 
    'average_buy_price', 
    'average_sell_price', 
    'buy_limit', 
    'sell_limit', 
    'matched_orders_volumne', 
    'matched_orders_value', 
    'total_orders_placed_buy', 
    'total_orders_placed_sell', 
    'total_volume_placed_buy', 
    'total_volume_placed_sell',
    'agreements_volumne',
    'agreements_value'
]

def download_data_to_dataframe(code, from_date="2021-01-01", to_date="2024-10-18", page_index=1, page_size=10):

    url = f"https://finance.vietstock.vn/data/ExportTradingResult?Code={code}&OrderBy=&OrderDirection=desc&PageIndex={page_index}&PageSize={page_size}&FromDate={from_date}&ToDate={to_date}&ExportType=excel&Cols=KLNY%2CKLCPDLH%2CGTC%2CT%2CS%2CTKLGD%2CTGTGD%2CVHTT%2CMC%2CTGG%2CLDM%2CDC%2CTGPTG%2CLDB%2CCN%2CBQM%2CLDMB%2CTN%2CBQB%2CKLDM%2CGYG%2CDM%2CKLDB%2CBQ%2CDB%2CKLDMB%2CGDC%2CKLGDKL%2CGTGDKL%2CKLGDTT%2CGTGDTT&ExchangeID=5"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'Referer': 'https://finance.vietstock.vn/ACV/thong-ke-giao-dich.htm',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        tables = soup.find_all("table")

        df = pd.read_html(str(tables[1]))[0] 
        return df
    else:
        print(f"Fail to get the data for {code}. Response status: {response.status_code}")
        return None

def insert_data_to_db(df, table_name, conn_str):
    engine = create_engine(conn_str)

    with engine.connect() as connection:
        for index, row in df.iterrows():

            query = text("""
                SELECT COUNT(*) FROM stock_data 
                WHERE trade_date = :trade_date AND stock_code = :stock_code
            """)
            result = connection.execute(query, {'trade_date': row['trade_date'], 'stock_code': row['stock_code']})
            count = result.scalar() 

            if count == 0:
                row.to_frame().T.to_sql(table_name, con=connection, if_exists='append', index=False)
            else:
                print(f"Duplicate entry for {row['trade_date']} and {row['stock_code']}, skipping.")

def update_database(ticker_list, from_date, to_date, conn_str):

    for ticker in ticker_list:

        print(f"Processing for {ticker}...")
        df = download_data_to_dataframe(ticker, from_date, to_date)

        if df is not None:

            df = df.drop(df.columns[[29, 26]], axis=1)
            df.columns = new_column_names
            df['trade_date'] = pd.to_datetime(df['trade_date'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
            df.insert(1, 'stock_code', ticker)
            df.replace("-", None, inplace=True)

            insert_data_to_db(df, table_name="stock_data", conn_str=conn_str)
            
            print (f"Insert data for {ticker} successfully!")
        else:
            print(f"No data found for {ticker}.")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'stock_data_update',
    default_args=default_args,
    description='A DAG to update stock data daily',
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:
    
    def run_update_database():
        conn_str = "postgresql+psycopg2://caokhoi:m6ikFt3TKwnkV75fNZ2FBdKiEHKEu1sN@dpg-cs87v7m8ii6s73c5m19g-a.singapore-postgres.render.com:5432/stock_data_01"

        from_date = "2021-01-01"
        to_date = datetime.today().strftime('%Y-%m-%d')

        update_database(ticker_list, from_date, to_date, conn_str)

    update_stock_data_task = PythonOperator(
        task_id='update_stock_data',
        python_callable=run_update_database,
    )

    update_stock_data_task
