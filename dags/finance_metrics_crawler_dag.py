from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import cloudscraper
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text

# Database connection and headers
DATABASE_CONN_STR = 'postgresql+psycopg2://caokhoi:m6ikFt3TKwnkV75fNZ2FBdKiEHKEu1sN@dpg-cs87v7m8ii6s73c5m19g-a.singapore-postgres.render.com:5432/stock_data_01'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
}

# Define translation dictionary
FIELD_TRANSLATION = {
    'NN mua': 'foreign_buy',
    '% NN sở hữu': 'percent_foreign_ownership',
    'Cổ tức TM': 'cash_dividend',
    'T/S cổ tức': 'dividend_yield',
    'Beta': 'beta',
    'EPS': 'eps',
    'P/E': 'pe',
    'F P/E': 'forward_pe',
    'BVPS': 'bvps',
    'P/B': 'pb'
}

# Define the function to fetch and insert data
def fetch_and_insert_stock_data():
    # Initialize the scraper and database engine
    scraper = cloudscraper.create_scraper()
    engine = create_engine(DATABASE_CONN_STR)
    
    # Fetch stock codes and URLs from `stock_info` table
    translated_data_list = []
    with engine.connect() as connection:
        query = text("SELECT code, url FROM stock_info")
        result = connection.execute(query)
        
        for row in result:
            print(f"Processing {row['code']}")
            # Fetch stock data
            response = scraper.get(row['url'], headers=HEADERS)
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract date and other stock info
            date_tag = soup.find('div', id='tradedate')
            date = date_tag.text.split()[0] if date_tag else "Unknown"
            table = soup.find('div', class_="row stock-price-info")
            data_dict = {}
            
            # Populate data_dict from parsed HTML data
            for div_class in ['col-xs-12 col-sm-5 col-md-4 col-c bg-50', 'col-xs-12 col-sm-4 col-md-4 col-c-last']:
                table_div = table.find('div', class_=div_class)
                if table_div:
                    fields = table_div.find_all('p', class_='p8')
                    for field in fields:
                        field_name = field.contents[0].strip() if field.contents else None
                        value_tag = field.find('b', class_='pull-right')
                        value = value_tag.text.strip().replace(',', '') if value_tag and value_tag.text.strip() != '-' else None
                        if field_name and value:
                            data_dict[FIELD_TRANSLATION.get(field_name, field_name)] = value

            # Prepare data for insertion
            translated_data_dict = {
                'stock_code': row['code'],
                'date': date,
                **data_dict
            }
            translated_data_list.append(translated_data_dict)
    
    # Insert data into `financial_metrics` table
    with engine.connect() as connection:
        for data in translated_data_list:
            insert_query = text("""
                INSERT INTO financial_metrics (stock_code, date, foreign_buy, percent_foreign_ownership, cash_dividend, dividend_yield, beta, eps, pe, forward_pe, bvps, pb)
                VALUES (:stock_code, :date, :foreign_buy, :percent_foreign_ownership, :cash_dividend, :dividend_yield, :beta, :eps, :pe, :forward_pe, :bvps, :pb)
                ON CONFLICT (stock_code, date) DO NOTHING;
            """)
            connection.execute(insert_query, data)

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'stock_data_crawler',
    default_args=default_args,
    description='Crawls stock data and inserts into database',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 11, 1),
    catchup=False,
) as dag:
    
    # Task to fetch and insert stock data
    crawl_and_store_data = PythonOperator(
        task_id='fetch_and_insert_stock_data',
        python_callable=fetch_and_insert_stock_data
    )

    crawl_and_store_data
