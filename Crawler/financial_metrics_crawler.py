# import cloudscraper
# from bs4 import BeautifulSoup
# from sqlalchemy import create_engine, text
# import concurrent.futures
# import gc
# from datetime import datetime

# # Define constants
# HEADERS = {
#     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Referer': 'https://www.google.com/',
#     'Cache-Control': 'no-cache',
#     'Pragma': 'no-cache',
#     'Connection': 'keep-alive',
# }

# FIELD_TRANSLATION = {
#     'NN mua': 'foreign_buy',
#     '% NN sở hữu': 'percent_foreign_ownership',
#     'Cổ tức TM': 'cash_dividend',
#     'T/S cổ tức': 'dividend_yield',
#     'Beta': 'beta',
#     'EPS': 'eps',
#     'P/E': 'pe',
#     'F P/E': 'forward_pe',
#     'BVPS': 'bvps',
#     'P/B': 'pb'
# }

# # Function to fetch stock data from the URL
# def get_stock_data(url):
#     scraper = cloudscraper.create_scraper()
#     response = scraper.get(url, headers=HEADERS)
#     soup = BeautifulSoup(response.text, "html.parser")

#     # Extract date
#     date_tag = soup.find('div', id='tradedate')
#     date = date_tag.text.split()[0] if date_tag else "Unknown"

#     # Extract stock information
#     table = soup.find('div', class_="row stock-price-info")
#     table_1 = table.find('div', class_='col-xs-12 col-sm-5 col-md-4 col-c bg-50')
#     table_2 = table.find('div', class_='col-xs-12 col-sm-4 col-md-4 col-c-last')
#     filtered_tables = [table_1, table_2]

#     data_dict = {}
#     for table in filtered_tables:
#         fields = table.find_all('p', class_='p8')
#         for field in fields:
#             field_name = field.contents[0].strip() if field.contents else None
#             value_tag = field.find('b', class_='pull-right')
#             value = value_tag.text.strip().replace(',', '') if value_tag and value_tag.text.strip() != '-' else None
            
#             if field_name and value:
#                 data_dict[FIELD_TRANSLATION.get(field_name, field_name)] = value

#     return date, data_dict

# conn_str = 'postgresql://stock_data_i36c_user:YLMLHhfjF7oIdi3SMzexVaobFuaL37Dc@dpg-csro9ppu0jms73e1epb0-a.singapore-postgres.render.com/stock_data_i36c'
# engine = create_engine(conn_str)


# # Create new table for financial metrics with camel case fields
# def create_financial_metrics_table(engine):
#     create_table_query = """
#     CREATE TABLE IF NOT EXISTS financial_metrics (
#         stock_code VARCHAR(20),
#         date DATE,
#         foreign_buy NUMERIC,
#         percent_foreign_ownership NUMERIC,
#         cash_dividend NUMERIC,
#         dividend_yield NUMERIC,
#         beta NUMERIC,
#         eps NUMERIC,
#         pe NUMERIC,
#         forward_pe NUMERIC,
#         bvps NUMERIC,
#         pb NUMERIC,
#         PRIMARY KEY (stock_code, date)
#     );
#     """
#     with engine.connect() as connection:
#         connection.execute(text(create_table_query))
# def convert_date_format(date_str):
#     try:
#         return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
#     except ValueError:
#         return None  # Return None if the date is invalid
    
# # Fetch stock codes and URLs, and integrate all data
# def process_stock_data(row):
#     try:
#         print(f"Processing for {row['code']}")
#         print(f"{row['url']}")
#         # Fetch data from the website
#         date, res_dict = get_stock_data(row['url'])

#         formatted_date = convert_date_format(date)

#         # Combine all data into a single dictionary
#         translated_data_dict = {
#             'stock_code': row['code'],
#             'date': formatted_date,
#             **res_dict  # Unpack the res_dict dictionary here
#         }

#         return translated_data_dict
#     except Exception as e:
#         print(f"Error processing data for {row['code']}: {e}")
#         return None
#     finally:
#         gc.collect()  # Ensure memory cleanup after each task

# # Insert data into the database
# def insert_financial_metrics_data(data_list):
#     try:
#         with engine.connect() as connection:
#             for data in data_list:
#                 if data:  # Proceed if data is not None
#                     insert_query = text("""
#                         INSERT INTO financial_metrics (stock_code, date, foreign_buy, percent_foreign_ownership, cash_dividend, dividend_yield, beta, eps, pe, forward_pe, bvps, pb)
#                         VALUES (:stock_code, :date, :foreign_buy, :foreign_ownership, :cash_dividend, :dividend_yield, :beta, :eps, :pe, :forward_pe, :bvps, :pb)
#                         ON CONFLICT (stock_code, date) DO NOTHING;  -- Prevents duplicate entries
#                     """)
#                     connection.execute(insert_query, {
#                         'stock_code': data['stock_code'],
#                         'date': data['date'],
#                         'foreign_buy': data.get('foreign_buy', None),
#                         'foreign_ownership': data.get('percent_foreign_ownership', None),
#                         'cash_dividend': data.get('cash_dividend', None),
#                         'dividend_yield': data.get('dividend_yield', None),
#                         'beta': data.get('beta', None),
#                         'eps': data.get('eps', None),
#                         'pe': data.get('pe', None),
#                         'forward_pe': data.get('forward_pe', None),
#                         'bvps': data.get('bvps', None),
#                         'pb': data.get('pb', None)
#                     })
#     except Exception as e:
#         print(f"Error inserting data into the financial_metrics table: {e}")
#     finally:
#         gc.collect()


# def main():
 
#     create_financial_metrics_table(engine)

#     try:
#         with engine.connect() as connection:
#             query = text("SELECT code, url FROM stock_info")
#             result = connection.execute(query)
#             rows = [row for row in result]

#             # Parallel processing using ThreadPoolExecutor
#             with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
#                 future_to_row = {executor.submit(process_stock_data, row): row for row in rows}
#                 translated_data_list = []

#                 for future in concurrent.futures.as_completed(future_to_row):
#                     data = future.result()
#                     if data:
#                         translated_data_list.append(data)

         
#                 insert_financial_metrics_data(translated_data_list)
#                 print("Financial metrics have been successfully inserted into the database.")

#     except Exception as e:
#         print(f"Error during main processing: {e}")

# if __name__ == "__main__":
#     main()

import logging
import cloudscraper
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

conn_str = 'postgresql://stock_data_i36c_user:YLMLHhfjF7oIdi3SMzexVaobFuaL37Dc@dpg-csro9ppu0jms73e1epb0-a.singapore-postgres.render.com/stock_data_i36c'

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

def convert_date_format(date_str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None  # Return None if the date is invalid
    

def fetch_stock_data(stock_code, url):

    scraper = cloudscraper.create_scraper()
    logging.info(f"Fetching data for stock code: {stock_code}")
    
    response = scraper.get(url, headers=HEADERS)

    if response.status_code != 200:
        logging.error(f"Failed to fetch data for {stock_code}. Status code: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    date_tag = soup.find('div', id='tradedate')
    date = date_tag.text.split()[0] if date_tag else "Unknown"


    table = soup.find('div', class_="row stock-price-info")


    data_dict = {}
    
    for div_class in ['col-xs-12 col-sm-5 col-md-4 col-c bg-50', 'col-xs-12 col-sm-4 col-md-4 col-c-last']:
        table_div = table.find('div', class_=div_class) if table else None
        if table_div:
            fields = table_div.find_all('p', class_='p8')

            for field in fields:
                field_name = field.contents[0].strip() if field.contents else None
                value_tag = field.find('b', class_='pull-right')
                value = value_tag.text.strip().replace(',', '') if value_tag and value_tag.text.strip() != '-' else None

                if field_name and value:
                    data_dict[FIELD_TRANSLATION.get(field_name, field_name)] = value
    
    data_dict = {
        'foreign_buy': data_dict.get('foreign_buy', '0'),
        'percent_foreign_ownership': data_dict.get('percent_foreign_ownership', '0'),
        'cash_dividend': data_dict.get('cash_dividend', '0'),
        'dividend_yield': data_dict.get('dividend_yield', '0'),
        'beta': data_dict.get('beta', '0'),
        'eps': data_dict.get('eps', '0'),
        'pe': data_dict.get('pe', '0'),
        'forward_pe': data_dict.get('forward_pe', '0'),
        'bvps': data_dict.get('bvps', '0'),
        'pb': data_dict.get('pb', '0')
    }
    logging.info(f"Data fetched for {stock_code}: {data_dict}")
    return {
        'stock_code': stock_code,
        'date': convert_date_format(date),
        **data_dict
    }

def insert_data_to_db(data, engine):
    if not data:
        return
    
    with engine.connect() as connection:
        insert_query = text("""
            INSERT INTO financial_metrics (stock_code, date, foreign_buy, percent_foreign_ownership, cash_dividend, dividend_yield, beta, eps, pe, forward_pe, bvps, pb)
            VALUES (:stock_code, :date, :foreign_buy, :percent_foreign_ownership, :cash_dividend, :dividend_yield, :beta, :eps, :pe, :forward_pe, :bvps, :pb)
            ON CONFLICT (stock_code, date) DO NOTHING;
        """)
        connection.execute(insert_query, data)
        logging.info(f"Data inserted for stock code: {data['stock_code']}")


def fetch_and_insert_stock_data():

    scraper = cloudscraper.create_scraper()
    engine = create_engine(conn_str)


    with engine.connect() as connection:
        query = text("SELECT code, url FROM stock_info")
        stock_list = connection.execute(query)
        
        with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust `max_workers` based on your needs
            futures = {executor.submit(fetch_stock_data, row['code'], row['url']): row['code'] for row in stock_list}
            for future in as_completed(futures):
                stock_code = futures[future]
                try:
                    data = future.result()
                    insert_data_to_db(data, engine)
                except Exception as e:
                    logging.error(f"Error processing stock code {stock_code}: {e}")

fetch_and_insert_stock_data()