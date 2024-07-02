
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import csv
import re
import time
import random

#instantiate the browser driver
s=Service(ChromeDriverManager().install())
o=Options()
o.add_argument("start-maximized")
driver = webdriver.Chrome(service=s, options=o)

# Set up CSV
csv_file = open('wholefoods_wine_test.csv', 'w', newline = '')
fieldnames = ['wine_name', 'winery','price','sale_price', 'valid_date']
writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
writer.writeheader()

# Go to the page to scrape
url = 'https://www.wholefoodsmarket.com/products/wine-beer-spirits/wine/red-wine'
driver.get(url)
time.sleep(random.randint(10,12)/10)

try:
    # Locate the search input field
    search_input = driver.find_element(By.ID, "pie-store-finder-modal-search-field")
    
    # Input the ZIP code and simulate pressing Enter
    search_input.send_keys("75010")
    search_input.send_keys(Keys.ENTER)
    
    # Wait for the results to load
    time.sleep(2)  # Adjust the sleep time as needed

    # Locate the desired list item by XPath
    desired_option = driver.find_element(By.XPATH, "//li[@class='wfm-search-bar--list_item' and span/text()='Plano - 2201 Preston Rd, Plano, TX 75093']")
    
    # Click the desired option
    desired_option.click()

except Exception as e:
    print(e)

# click load more results to load more
for i in range(0,5):
    try:
        # Locate the button using its CSS selector
        load_more_button = driver.find_element(By.XPATH, "//button[@class = 'w-button w-button--secondary w-button--load-more' and @data-testid='load-more-button']")

        # Scroll down until the button is in view
        #driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
        driver.execute_script('window.scrollBy(0, 1000)')
        load_more_button.click()

        # Wait for a short period to ensure the button is in view
        time.sleep(1)

    except Exception as e:
        print(e)

# Wait until the product elements are present in the DOM
all_urls = driver.find_elements(By.XPATH, ".//div[@class='w-pie--product-tile']")

# Extract URLs, wine name, winery, price from each product element
all_str_urls = []
for element in all_urls:
    url = element.find_element(By.XPATH, ".//a[@class='w-pie--product-tile__link']").get_attribute('href')
    all_str_urls.append(url)

wine_dict = {}
try:
    # Find all product tiles
    product_tiles = driver.find_elements(By.XPATH, ".//div[@class='w-pie--product-tile']")

    for tile in product_tiles:
        content = tile.find_element(By.XPATH, ".//div[@class='w-pie--product-tile__content']")
        image = tile.find_element(By.XPATH, ".//div[@class='w-pie--product-tile__image']")
        sale_badge_elements = tile.find_elements(By.XPATH, ".//span[@class='w-pie--badge w-pie--badge__sale']")
            
        # Find the brand name within each product tile
        wine_element = content.find_element(By.XPATH, ".//span[@class='w-cms--font-disclaimer' and @data-testid='product-tile-brand']")
        wine_name = wine_element.text.strip()
        winery_element = content.find_element(By.XPATH, ".//h2[@class='w-cms--font-body__sans-bold' and @data-testid='product-tile-name']")
        winery_name = winery_element.text.strip()

        if len(sale_badge_elements) != 0:
            # Find the valid date
            try:
                valid_date_element = image.find_element(By.XPATH, ".//div[@class='w-pie--product-tile__valid-date' and @data-testid='valid-date']")
                valid_date = valid_date_element.text.strip()
            except NoSuchElementException:
                print("Valid date not found.")
            
            # Find the sale price
            try:
                sale_price_element = content.find_element(By.XPATH, ".//div[@class='bds--heading-5 mr-1 inline px-1 !text-base bg-citron']")
                sale_price = sale_price_element.text.strip()
            except NoSuchElementException:
                print("Sale price not found.")
            
            # Find the regular price
            try:
                price_element = content.find_element(By.XPATH, ".//span[@class='text-left text-base !font-thin text-chia-seed line-through']")
                price = price_element.text.strip()
            except NoSuchElementException:
                print("Regular price not found.")
        else:
            price_element = content.find_element(By.XPATH, ".//span[@class='text-left bds--heading-5']")
            price = price_element.text.strip()
            valid_date = 'N/A'
            sale_price = '$0'
        
        # Define wine_dict and assign each element
        wine_dict['wine_name'] = wine_name
        wine_dict['winery'] = winery_name
        wine_dict['price'] = price
        wine_dict['sale_price'] = sale_price
        wine_dict['valid_date'] = valid_date

        try:
            writer.writerow(wine_dict)
        except Exception as e:
            print(e)
            pass
        

finally:
    # Close the driver
    driver.quit()

print(len(all_str_urls))
csv_file.close()