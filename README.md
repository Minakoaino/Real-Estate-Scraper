# Real Estate Scraper

Real Estate Scraper is a Python application designed to scrape real estate listing data from www.realestate.com.au. It navigates to the pages selected by the user and scrapes data, including property ID, price, property type, address, number of bedrooms and bathrooms, house size, image link, and property link. The data is then saved to a CSV file and a SQLite database.

This application consists of two main steps:

1. **Data Scraping**: Navigates to the real estate website and scrapes the required data. It uses Selenium WebDriver for navigation and BeautifulSoup for parsing and extracting the data.

2. **Data Storage**: Saves the scraped data to a CSV file and a SQLite database. It uses pandas for data manipulation and SQLAlchemy for database operations.

3. **Navigating to Listing Pages**: Navigates to every single scraped listing page to retrieve the images and additional data.

## :rocket: Getting Started

To start using this scraper, you will need Python 3.8 or newer. You will also need to install the following Python packages: Selenium, BeautifulSoup, Pandas, SQLAlchemy, and pyodbc. You can install these packages using pip:


```sh
pip install selenium beautifulsoup4 pandas sqlalchemy pyodbc
```

## :bookmark_tabs: Prerequisites

- Python (3.8 or higher)
- Selenium
- BeautifulSoup
- Pandas
- SQLAlchemy
- pyodbc

Additionally, you will need a Selenium WebDriver to run this program. You can download the latest version of the WebDriver for your browser from the [Selenium website](https://www.selenium.dev/downloads/). Please make sure that the WebDriver is installed in a location that is on your system's PATH.

## :inbox_tray: Installation

1. Clone this repository to your local machine.

```
git clone https://github.com/your_username/real_estate_scraper.git
```

Change directory to the local clone of this repository.

```
cd real_estate_scraper
```

Install the required packages.

```
pip install -r requirements.txt
```
Download the latest version of Selenium WebDriver for your browser. Install the WebDriver in a location that is on your system's PATH.

:computer: Usage
To use the scraper, simply run the scripts:

```
python scrape_real_estate_data.py
```

Once the first script finishes running, you can run the second script:

```
python get_images.py
```

The scraper will then start scraping the selected pages of the real estate website. If the script is interrupted, it will automatically save the scraped data to a CSV file and the database.
