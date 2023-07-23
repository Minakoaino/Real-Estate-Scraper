import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from urllib.parse import urlparse
import re 
from selenium.webdriver.chrome.options import Options
import time
import requests
import sys
#we import our previous file in order to get some functions
from scrape_real_estate_data import save_data_to_csv
from scrape_real_estate_data import save_data_to_db


# Set up Selenium WebDriver
options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)
# Create a directory to store the downloaded images if it does not exist
output_directory = 'scraped_images'
os.makedirs(output_directory, exist_ok=True)

# Read the CSV file into a DataFrame
df = pd.read_csv('scrape_data.csv')

# Extract the URLs and IDs from the DataFrame
urls = df['propertyLink']
ids = df['Id']
details_list = []
image_urls = []  # Store the image URLs

# Iterate over the URLs and IDs
# for url, item_id in zip(urls, ids): --first run
for url, item_id in zip(urls, ids):
    
    # Define DB filename and table names
    db_file = 'real_estate_db'
    table_name_csv = 'image_data'
    table_name_exception = 'image_data'
        
    try:
        driver.get(url)
        # Add a delay of 2 seconds
        time.sleep(6)
        # Extract the page source
        page_source = driver.page_source

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find the first class containing the images
        first_class = soup.find(class_='thumbnails')
        if first_class is not None:
            # Find all <img> tags in the first class
            first_class_images = first_class.find_all('img')
        else:
            first_class_images = []

        # Find the second class containing the images
        second_class = soup.find(class_='poster')
        if second_class is not None:
            # Find the <img> tag in the second class
            second_class_image = second_class.find('img')
            if second_class_image is not None:
                second_class_images = [second_class_image]
            else:
                second_class_images = []
        else:
            second_class_images = []

        # Combine the images from both classes
        all_images = first_class_images + second_class_images

        # Extract the image URLs
        image_urls_row = [img['src'] for img in all_images]
        modified_urls = []
        for url in image_urls_row:
            modified_url = url.replace("250x160-", "1208x680-")
            modified_url = "https:" + modified_url  # Prepend with valid scheme
            modified_urls.append(modified_url)
            
            # Prepend the scheme to the modified URL if missing
            if modified_url.startswith('//'):
                modified_url = f"https:{modified_url}"      
                modified_urls.append(modified_url)
                
        image_urls_str = ';'.join(modified_urls) if modified_urls else '0'            
                
        # Download and save each image
        for i, img in enumerate(all_images):
            modified_url = modified_urls[i]  # Get the corresponding modified URL
            # Prepend the scheme to the modified URL if missing
            if not modified_url.startswith(('http://', 'https://')):
                modified_url = f"https:{modified_url}"
            modified_url = modified_urls[i]  # Get the corresponding modified URL
            # Extract the filename from the URL
            filename = f"{item_id}_{i}.jpg"

            # Check if the image already exists in the directory
            if not os.path.isfile(os.path.join(output_directory, filename)):
                # Download the image
            # Download the image
                response = requests.get(modified_url)
                # Extract the filename from the URL
                filename = f"{item_id}_{i}.jpg"
                # Save the image to the output directory
                with open(os.path.join(output_directory, filename), 'wb') as img_file:
                    img_file.write(response.content)

        # Print the modified image URLs
        for url in image_urls_row:
            print(url)
            
        # Find the property ID
        property_id_element = soup.find(class_='listing-id')
        property_id = property_id_element.text.strip() if property_id_element is not None else 'N/A'

        # Find the agency name and address and telephone (the telephone will be masked)
        agency_name_element = soup.find(class_='agency-name')
        agency_name = agency_name_element.text.strip() if agency_name_element is not None else 'N/A'

        agency_address_element = soup.find(class_='agency-address')
        agency_address = agency_address_element.text.strip() if agency_address_element is not None else 'N/A'

        agent_telephone_element = soup.find(class_='yy9d2l-0 jpIXJp')
        agent_telephone = agent_telephone_element.text.strip() if agent_telephone_element is not None else 'N/A'

        agent_phone_element = soup.find('a', class_='agent-officephone')
        agent_phone = agent_phone_element.text.strip() if agent_phone_element is not None else 'N/A'

        # Find the listing details class
        listing_details = soup.find(class_='property-description') 
        listing_text = listing_details.text.strip() if listing_details is not None else 'N/A'

        # Find the property details
        property_details_element = soup.find(class_='zs0kp9-8')
        property_details = property_details_element.text.strip() if property_details_element is not None else 'N/A'

        # Find the div with class "google-map-box-fullHeight"
        time.sleep(10)
        map_div = soup.find('div', class_='google-map-box-fullHeight')
        # Extract the href attribute value
        href = map_div.a['href'] if map_div and map_div.a is not None else 'N/A'

        # Extract the latitude and longitude from the href using regular expressions
        matches = re.findall(r'll=([-+]?\d+\.\d+),([-+]?\d+\.\d+)', href)
        if matches:
            latitude, longitude = matches[0]
        else:
            latitude, longitude = 'N/A', 'N/A'

        ## published on modified on    
        data_div = soup.find(class_='data')
        # Initialize the published on and last updated on variables
        published_on = None
        last_updated_on = None

        # Find the div elements within the data div
        # Initialize div_elements
        div_elements = []
        if data_div is not None:
            div_elements = data_div.find_all('div')

        # Extract the published on and last updated on details
        for div in div_elements:
            span = div.find('span', class_='title')
            if span:
                if span.text.strip() == 'Published on':
                    published_on = div.text.split(':')[-1].strip()
                elif span.text.strip() == 'Last updated on':
                    last_updated_on = div.text.split(':')[-1].strip()

        # # Create a dictionary with the details
        details_dict = {
            'Published on': published_on if published_on is not None else 'N/A',
            'Last updated on': last_updated_on if last_updated_on is not None else 'N/A'
        }


        # Print the details
        for key, value in details_dict.items():
            print(f"{key}: {value}")
     
        # Store all the details in a dictionary
        details_dict = {
            'Id': item_id,
            'Property ID': property_id,
            'Listing Details': listing_text,
            'Agent Name': agency_name,
            'Agent Telephone' : agent_telephone,
            'Latitude': latitude,
            'Longitude': longitude,        
            'Agency Name': agency_name,
            'Agency Address': agency_address,
            'Published on' : published_on,
            'Last updated on' : last_updated_on,
            'Image URLs': image_urls_str      # Add the image URLs to the dictionary

        }
        
        # Print the published on and last updated on details
        print(f"Published on: {published_on}")
        print(f"Last updated on: {last_updated_on}")
        # Print the listing details, agent name, latitude/longitude, agency name, and agency address
        print(f"Listing Details for ID {item_id}: {listing_text}")
        print(f"Agent Name: {agency_name}")
        print(f"Agent Telephone: {agent_telephone}")    
        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")
        print(f"Agency Name: {agency_name}")
        print(f"Agency Address: {agency_address}")
        print(f"Published on:{published_on}")
        print(f"Last updated on: {last_updated_on}")
        
        # Add the details to the list
        details_list.append(details_dict)           
        filename = 'images.csv'
        # Create a DataFrame from the details list
        details_df = pd.DataFrame(details_list)
        # After successful execution of your web scraping code we save in a db and csv file:
        filename = 'images.csv'
        # Now, call the function with necessary parameters
        details_df = save_data_to_csv(details_list, filename)
        # Save to DB
        save_data_to_db(details_df, db_file, table_name_csv)
        print("Data saved to file.")
        # Then you can close your webdriver
        driver.quit()

    except KeyboardInterrupt:
        print("Interrupted by user. Saving current data to file...")
        filename = 'images.csv'
        # Save data to CSV
        details_df = save_data_to_csv(details_list, filename)
        # Save data to DB
        save_data_to_db(details_df, db_file, table_name_exception)
        print("Data saved to file.")
        driver.quit()
        sys.exit(0)