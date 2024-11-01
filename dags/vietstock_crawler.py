import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()

url = 'https://vietstock.vn/chung-khoan.htm'

try:
    response = scraper.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        links = [a['href'] for a in soup.find_all('a', href=True)]
        
        print("Found links:")
        for link in links:
            print(link)
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

except Exception as e:
    print(f"An error occurred: {e}")
