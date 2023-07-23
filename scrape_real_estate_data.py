import os
import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from sqlalchemy import create_engine

def create_webdriver():
    options = Options()
    options.add_argument("--log-level=3")  
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def navigate_to_page(driver, url):
    driver.get(url)

def scrape_data(driver, pages, filename):
    data = []
    current_page = 1

    try:
        while current_page <= pages:
            time.sleep(3)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            listings = soup.find_all('li', class_='listing')

            for listing in listings:
                data.append(extract_data(listing))

            print(pd.DataFrame(data))

            next_button = driver.find_element(By.CSS_SELECTOR, 'a.next')
            if next_button and 'inactive' not in next_button.get_attribute('class'):
                next_button.click()
                time.sleep(30)
                current_page += 1
            else:
                break
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        details_df = pd.DataFrame(data)
        save_data_to_csv(details_df, filename)
        return data

def extract_data(listing):
    propertyid_element = listing.find('a', class_='btn listing-link button')
    href = propertyid_element['href']
    digits = re.findall(r'\d+', href)
    data = {
        'Id': digits,
        'Price': extract_element_text(listing, 'p', 'listing-price specified', 'N/A'),
        'property_Type': extract_element_text(listing, 'div', 'propertytype', 'N/A'),
        'Address': extract_address(listing),
        'Bedrooms': extract_element_strong(listing, 'li', 'Bedrooms', 'N/A'),
        'Bathrooms': extract_element_strong(listing, 'li', 'Bathrooms', 'N/A'),
        'House_Size': extract_element_strong(listing, 'li', 'House Size', 'N/A'),
        'Image_Link': extract_image_link(listing),
        'propertyLink': f"https://www.realestate.com.au{propertyid_element['href']}" if propertyid_element else 'N/A'
    }
    return data


def extract_element_text(listing, tag, class_name, default):
    element = listing.find(tag, class_=class_name)
    return element.text.strip() if element else default


def extract_element_strong(listing, tag, title, default):
    element = listing.find(tag, title=title)
    return element.find('strong').text.strip() if element else default


def extract_address(listing):
    address_element = listing.find('address', class_='address')
    return address_element.find('a').text.strip() if address_element else 'N/A'


def extract_image_link(listing):
    image_link_element = listing.find('img', class_='lazy lazy-loaded')
    return image_link_element['src'] if image_link_element else 'N/A'


def save_data_to_csv(data, filename):
    details_df = pd.DataFrame(data)
    if os.path.isfile(filename):
        details_df.to_csv(filename, mode='a', header=False, index=False)
    else:
        details_df.to_csv(filename, index=False)
    return details_df


def save_data_to_db(details_df, db_file, table_name):
    # Create the SQLAlchemy engine
    engine = create_engine(f'sqlite:///{db_file}')
    # Adjust details_df and store it into the database
    details_df['Id'] = details_df['Id'].astype(str)
    details_df['Id'] = details_df['Id'].str.replace('[', '').str.replace(']', '').str.replace("'", "")
    details_df.to_sql(table_name, con=engine, if_exists='append', index=False)
    print(details_df)
    existing_ids_df = pd.read_sql_query(f"SELECT Id FROM {table_name}", engine)
    if isinstance(details_df['Id'].iloc[0], list):
        details_df['Id'] = details_df['Id'].apply(lambda x: ','.join(map(str, x)))
    existing_ids = set(existing_ids_df['Id'])
    new_ids = set(details_df['Id'])
    unique_ids = new_ids - existing_ids
    details_df_unique = details_df[details_df['Id'].isin(unique_ids)]
    details_df_unique.to_sql(table_name, con=engine, if_exists='append', index=False)
    engine.dispose()
    return details_df

def main():
    url = "https://www.realestate.com.au/international/gr/attica/"
    filename = 'scrape_data.csv'
    db_file = 'real_estate_db.db'  # SQLite will create this file in the current directory if it doesn't exist
    table_name = 'realestate_au'

    driver = create_webdriver()
    navigate_to_page(driver, url)
    data = scrape_data(driver,pages=2, filename=filename)
    details_df = save_data_to_csv(data, filename)
    details_df = save_data_to_db(details_df, db_file, table_name)
    print(details_df)


if __name__ == "__main__":
    main()