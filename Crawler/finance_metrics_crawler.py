import cloudscraper
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
import concurrent.futures
import gc
from datetime import datetime

# Define constants
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Connection': 'keep-alive',
}

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

# Function to fetch stock data from the URL
def get_stock_data(url):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract date
    date_tag = soup.find('div', id='tradedate')
    date = date_tag.text.split()[0] if date_tag else "Unknown"

    # Extract stock information
    table = soup.find('div', class_="row stock-price-info")
    table_1 = table.find('div', class_='col-xs-12 col-sm-5 col-md-4 col-c bg-50')
    table_2 = table.find('div', class_='col-xs-12 col-sm-4 col-md-4 col-c-last')
    filtered_tables = [table_1, table_2]

    data_dict = {}
    for table in filtered_tables:
        fields = table.find_all('p', class_='p8')
        for field in fields:
            field_name = field.contents[0].strip() if field.contents else None
            value_tag = field.find('b', class_='pull-right')
            value = value_tag.text.strip().replace(',', '') if value_tag and value_tag.text.strip() != '-' else None
            
            if field_name and value:
                data_dict[FIELD_TRANSLATION.get(field_name, field_name)] = value

    return date, data_dict

# Initialize database connection
conn_str = 'postgresql+psycopg2://caokhoi:m6ikFt3TKwnkV75fNZ2FBdKiEHKEu1sN@dpg-cs87v7m8ii6s73c5m19g-a.singapore-postgres.render.com:5432/stock_data_01'
engine = create_engine(conn_str)

# Create new table for financial metrics with camel case fields
def create_financial_metrics_table(engine):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS financial_metrics (
        stock_code VARCHAR(20),
        date DATE,
        foreign_buy NUMERIC,
        percent_foreign_ownership NUMERIC,
        cash_dividend NUMERIC,
        dividend_yield NUMERIC,
        beta NUMERIC,
        eps NUMERIC,
        pe NUMERIC,
        forward_pe NUMERIC,
        bvps NUMERIC,
        pb NUMERIC,
        PRIMARY KEY (stock_code, date)
    );
    """
    with engine.connect() as connection:
        connection.execute(text(create_table_query))
def convert_date_format(date_str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None  # Return None if the date is invalid
    
# Fetch stock codes and URLs, and integrate all data
def process_stock_data(row):
    try:
        print(f"Processing for {row['code']}")
        print(f"{row['url']}")
        # Fetch data from the website
        date, res_dict = get_stock_data(row['url'])

        formatted_date = convert_date_format(date)

        # Combine all data into a single dictionary
        translated_data_dict = {
            'stock_code': row['code'],
            'date': formatted_date,
            **res_dict  # Unpack the res_dict dictionary here
        }

        return translated_data_dict
    except Exception as e:
        print(f"Error processing data for {row['code']}: {e}")
        return None
    finally:
        gc.collect()  # Ensure memory cleanup after each task

# Insert data into the database
def insert_financial_metrics_data(data_list):
    try:
        with engine.connect() as connection:
            for data in data_list:
                if data:  # Proceed if data is not None
                    insert_query = text("""
                        INSERT INTO financial_metrics (stock_code, date, foreign_buy, percent_foreign_ownership, cash_dividend, dividend_yield, beta, eps, pe, forward_pe, bvps, pb)
                        VALUES (:stock_code, :date, :foreign_buy, :foreign_ownership, :cash_dividend, :dividend_yield, :beta, :eps, :pe, :forward_pe, :bvps, :pb)
                        ON CONFLICT (stock_code, date) DO NOTHING;  -- Prevents duplicate entries
                    """)
                    connection.execute(insert_query, {
                        'stock_code': data['stock_code'],
                        'date': data['date'],
                        'foreign_buy': data.get('foreign_buy', None),
                        'foreign_ownership': data.get('percent_foreign_ownership', None),
                        'cash_dividend': data.get('cash_dividend', None),
                        'dividend_yield': data.get('dividend_yield', None),
                        'beta': data.get('beta', None),
                        'eps': data.get('eps', None),
                        'pe': data.get('pe', None),
                        'forward_pe': data.get('forward_pe', None),
                        'bvps': data.get('bvps', None),
                        'pb': data.get('pb', None)
                    })
    except Exception as e:
        print(f"Error inserting data into the financial_metrics table: {e}")
    finally:
        gc.collect()


def main():
 
    create_financial_metrics_table(engine)

    try:
        with engine.connect() as connection:
            query = text("SELECT code, url FROM stock_info")
            result = connection.execute(query)
            rows = [row for row in result]

            # Parallel processing using ThreadPoolExecutor
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_row = {executor.submit(process_stock_data, row): row for row in rows}
                translated_data_list = []

                for future in concurrent.futures.as_completed(future_to_row):
                    data = future.result()
                    if data:
                        translated_data_list.append(data)

         
                insert_financial_metrics_data(translated_data_list)
                print("Financial metrics have been successfully inserted into the database.")

    except Exception as e:
        print(f"Error during main processing: {e}")

if __name__ == "__main__":
    main()
