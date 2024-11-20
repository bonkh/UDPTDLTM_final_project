
import re
import requests
import pandas as pd
import logging
import time
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from datetime import datetime
from newspaper import Article
import urllib.request
from urllib.error import URLError
from sqlalchemy.dialects.postgresql import insert
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

conn_str = 'postgresql://stock_data_i36c_user:YLMLHhfjF7oIdi3SMzexVaobFuaL37Dc@dpg-csro9ppu0jms73e1epb0-a.singapore-postgres.render.com/stock_data_i36c'
engine = create_engine(conn_str)


def fetch_page(url, retries=3, delay=3):
    for attempt in range(retries):
        try:
            page = urllib.request.urlopen(url, timeout=10)
            return page
        except URLError as e:
            logging.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            time.sleep(delay)
    logging.error(f"Failed to fetch {url} after {retries} attempts.")
    return None

def get_links_in_page_vnexpress(url):
    try:
        page = fetch_page(url)
        if page is None:
            logging.error(f"Failed to fetch page {url}")
            return []

        soup = BeautifulSoup(page, 'html.parser')
        sections = soup.find_all('section', attrs={'class': 'section section_container mt15'})

        links = []
        for section in sections:
            titles = section.find_all('h2', attrs={'class': 'title-news'})
            for title in titles:
                a = title.find('a')
                if a:
                    link = a.get('href')
                    title_text = a.get('title')
                    if title_text and link:
                        links.append({'title': title_text, 'link': link})
                        logging.info(f"Found title: {title_text} - Link: {link}")
        return links
    except Exception as e:
        logging.error(f"Error parsing links from page {url}: {e}")
        return []

def get_links():
    news_list = []
    urls = [f'https://vnexpress.net/kinh-doanh/chung-khoan-p{i}' for i in range(1, 21)]

    for url in urls:
        try: 
            news_list.extend(get_links_in_page_vnexpress(url))
        except Exception as e:
            logging.error(f"Error fetching links from {url}: {e}")

    df = pd.DataFrame(news_list).drop_duplicates(subset=['link']).reset_index(drop=True)
    return df

def normalize_date(date_str):
    try:
        date = date_str.split(',')[1].strip()
        parsed_date = pd.to_datetime(date, format='%d/%m/%Y')
        return parsed_date.strftime('%Y-%m-%d')
    except Exception as e:
        logging.error(f"Error normalizing date: {date_str}, {e}")
        return None

def crawl_by_url(url, retries=3, backoff_factor=0.3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, allow_redirects=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                if soup.find('span', class_='date'):
                    date = soup.find('span', class_='date').text
                    date = normalize_date(date)
                else :
                    date = None

                article = Article(url, language='vi')
                article.set_html(response.text)
                article.download(input_html=response.text)
                article.parse()

                content = str(article.text).strip()
                return {'link': url, 'date': date, 'content': content}
            else:
                logging.error(f"Failed to crawl {url}, status code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Error during crawling {url}: {e}")
            time.sleep(backoff_factor * (2 ** attempt))
    return None


def get_existing_links():

    try:
        query = "SELECT link FROM article"
        with engine.connect() as connection:
            result = connection.execute(query)
            existing_links = {row['link'] for row in result}
        return existing_links
    except Exception as e:
        logging.error(f"Error fetching existing links: {e}")
        return set()

def filter_new_links(all_links, existing_links):

    try:
        all_links_set = set(all_links)
        new_links = all_links_set - existing_links
        return list(new_links)
    except Exception as e:
        logging.error(f"Error filtering new links: {e}")
        return []

def insert_articles_to_db(new_articles_df):
    try:
        with engine.connect() as connection:
            for _, row in new_articles_df.iterrows():
                insert_query = """
                INSERT INTO article (title, link, content, date)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (title, date) DO NOTHING
                """
                try:
                    connection.execute(insert_query, (row['title'], row['link'], row['content'], row['date']))
                except Exception as e:
                    print(f"Error inserting article '{row['title']}' into the database: {e}")
        print("Insertion completed with row-by-row conflict handling.")
    except Exception as e:
        print(f"Error in database insertion process: {e}")

def count_articles():
    with engine.connect() as connection:
        result = connection.execute("SELECT COUNT(*) FROM article")
        count = result.scalar()
    return count

def crawl_and_save_new_links(new_links):

    try:
        data_to_insert = [] 

        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit the crawl tasks to the executor
            future_to_url = {executor.submit(crawl_by_url, link): link for link in new_links}
            
            # Process the results as they are completed
            for future in as_completed(future_to_url):
                link = future_to_url[future]
                try:
                    result = future.result()
                    if result['date'] and result['content']:
                        data_to_insert.append(result)
                    else:
                        logging.warning(f"No content for link {link}")
                except Exception as e:
                    logging.error(f"Error crawling {link}: {e}")
    
        if data_to_insert:
            new_articles_df = pd.DataFrame(data_to_insert)
          
            insert_articles_to_db(new_articles_df)
        else:
            logging.info("No valid data to insert.")

    except Exception as e:
        logging.error(f"Error during crawling and saving new links: {e}")

def main():
    try:
        initial_count = count_articles()
        print(initial_count)
        all_links_df = get_links()
        all_links = all_links_df['link'].tolist()
        existing_links = get_existing_links()
        new_links = filter_new_links(all_links, existing_links)
        
        if new_links:
            logging.info(f"Found {len(new_links)} new links to crawl.")
            crawl_and_save_new_links(new_links)
        else:
            logging.info("No new links to process.")
        
        logging.info("Insertion completed.")

        final_count = count_articles()
        logging.info(f"Final article count: {final_count}")

        inserted_count = final_count - initial_count
        logging.info(f"Number of articles inserted: {inserted_count}")

    except Exception as e:
        logging.error(f"Error in main execution: {e}")


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'vnexpress_article_crawler',
    default_args=default_args,
    description='VnExpress article crawling DAG',
    schedule_interval='0 0 * * *',
    start_date=datetime(2024, 10, 1, 0, 0),
)

# Define the tasks
crawl_task = PythonOperator(
    task_id='vnexpress_article_crawler',
    python_callable=main,
    dag=dag,
)

crawl_task
