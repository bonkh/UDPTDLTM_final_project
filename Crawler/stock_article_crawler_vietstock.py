import pandas as pd
import gc
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Database connection setup
engine = create_engine('postgresql+psycopg2://caokhoi:m6ikFt3TKwnkV75fNZ2FBdKiEHKEu1sN@dpg-cs87v7m8ii6s73c5m19g-a.singapore-postgres.render.com:5432/stock_data_01')

# Function to get existing articles from the database
def get_existing_articles():
    try:
        query = "SELECT title, date FROM article"
        with engine.connect() as connection:
            result = connection.execute(query)
            return set((row['title'], row['date']) for row in result)
    except SQLAlchemyError as e:
        logging.error(f"Error retrieving existing articles from the database: {e}")
        return set()  # Return an empty set if there's an error



def scrape_urls():
    chrome_options = Options()
    chrome_options.add_argument("--start-fullscreen")
    url_list = []
    browser = None

    try:
        browser = webdriver.Chrome(options=chrome_options)
        browser.get('https://vietstock.vn/chung-khoan.htm')
        
        for i in range(1, 200):
            sleep(2)
            # Get links from the current page
            a_fontbold = browser.find_elements(By.CSS_SELECTOR, 'a.fontbold')
            hrefs = [element.get_attribute("href") for element in a_fontbold]
            url_list.extend(hrefs)
            
            # Click on the "Next" button to go to the next page
            try:
                next_button = browser.find_element(By.CSS_SELECTOR, 'a[title="Trang sau"]')
                ActionChains(browser).move_to_element(next_button).click().perform()
            except Exception as e:
                logging.info("Reached the last page or encountered an error while navigating: {}".format(e))
                break
    except Exception as e:
        logging.error(f"Error while scraping URLs: {e}")
    finally:
        if browser:
            browser.quit()

    # Remove duplicates
    url_list = list(set(url_list))
    return url_list


def extract_article_content(url_list):
    news_data = []
    browser = None

    try:
        browser = webdriver.Chrome()
        for url in url_list:
            try:
                browser.get(url)
                sleep(2)
                title = browser.find_element(By.CSS_SELECTOR, 'h1[class="article-title"]').text
                date = browser.find_element(By.CSS_SELECTOR, 'span[class="date"]').text
                content_elements = browser.find_elements(By.CSS_SELECTOR, 'p[class="pBody"]')
                content = ' '.join([element.text for element in content_elements])
                news_data.append([title, url, content, date])
            except Exception as e:
                logging.error(f"Error scraping {url}: {e}")
                continue
    except Exception as e:
        logging.error(f"Error in article extraction process: {e}")
    finally:
        if browser:
            browser.quit()
    
    # Convert to DataFrame
    news_df = pd.DataFrame(news_data, columns=['title', 'link', 'content', 'date'])
    return news_df



def filter_new_articles(news_df):
    try:
        existing_articles = get_existing_articles()
        # Ensure date format consistency and strip any extra spaces in title
        news_df['date'] = pd.to_datetime(news_df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
        news_df['title'] = news_df['title'].str.strip()

        # Only keep rows where title-date pairs are not in existing_articles
        new_articles_df = news_df[~news_df[['title', 'date']].apply(tuple, axis=1).isin(existing_articles)]
        return new_articles_df
    
    except Exception as e:
        logging.error(f"Error filtering new articles: {e}")
        return news_df

def insert_articles_to_db(new_articles_df):
    try:
        with engine.connect() as connection:
            for _, row in new_articles_df.iterrows():
                insert_query = """
                INSERT INTO article (title, link, content, date)
                VALUES (%s, %s, %s, %s)
                """
                try:
                    connection.execute(insert_query, (row['title'], row['link'], row['content'], row['date']))
                except Exception as e:
                    logging.error(f"Error inserting article '{row['title']}' into the database: {e}")
    except SQLAlchemyError as e:
        logging.error(f"Error in database insertion process: {e}")


def count_articles():
    with engine.connect() as connection:
        result = connection.execute("SELECT COUNT(*) FROM article")
        count = result.scalar()
    return count

# Main Process
def main():
    try:
        initial_count = count_articles()
        print(f"Intitial amount of articles: {initial_count}")

        url_list = scrape_urls()
        news_df = extract_article_content(url_list)
        new_articles_df = filter_new_articles(news_df)
        logging.info(f"New articles to insert: {new_articles_df.shape[0]}")

        if not new_articles_df.empty:
            insert_articles_to_db(new_articles_df)
            logging.info("New articles inserted into the database successfully.")

            final_count = count_articles()
            logging.info(f"Final article count: {final_count}")

            inserted_count = final_count - initial_count
            logging.info(f"Number of articles inserted: {inserted_count}")

        else:
            logging.info("No new articles to insert.")
    except Exception as e:
        logging.error(f"An error occurred in the main process: {e}")
    finally:
        gc.collect()

if __name__ == "__main__":
    main()