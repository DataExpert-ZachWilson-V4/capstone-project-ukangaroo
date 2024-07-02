
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
import pandas as pd
import csv
import re
import time
import random

#instantiate the browser driver
s=Service(ChromeDriverManager().install())
o=Options()
o.add_argument("start-maximized")
driver = webdriver.Chrome(service=s, options=o)

# Set up action chains
actions = ActionChains(driver)

# Define function to find the metrics
def find_metrics(driver, wine_dict):

    metric_dict = {"Light": "light_bold",
                   "Smooth": "smooth_tannic",
                   "Dry": "dry_sweet",
                   "Soft": "soft_acidic"}
    
    all_metric_names = driver.find_elements(By.XPATH, '//tr[@class="tasteStructure__tasteCharacteristic--jLtsE"]/td/div[@class="tasteStructure__property--CLNl_"]')
    selected_metric_names = [all_metric_names[i].text for i in range(len(all_metric_names)) if i%2 == 0]
    final_metric_names = [metric_dict[key] for key in selected_metric_names]
    missing_metric_names = list(set(metric_dict.values()) - set(final_metric_names))
    
    all_metrics_prep = driver.find_elements(By.XPATH, '//div[@class="indicatorBar__meter--2t_YL tasteStructure__progressBar--HGIje"]/span[@class="indicatorBar__progress--3aXLX"]')
    all_metrics = [float(re.findall('\d*\.?\d+',all_metrics_prep[i].get_attribute('style'))[1]) for i in range(len(all_metrics_prep))]
    
    if len(missing_metric_names) > 0:
        for i in missing_metric_names:
            wine_dict[i] = -1

    for i,j in zip(final_metric_names, all_metrics):
        wine_dict[i] = j
    
    return wine_dict

# Set up CSV
csv_file = open('vivino_wine_frompg28.csv', 'w', newline = '')
fieldnames = ['winery','wine_type','city','country','wine_name','year','overall_rating','overall_rating_count',\
              'price','light_bold','smooth_tannic','dry_sweet','soft_acidic']
writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
writer.writeheader()

# Bring in the pages that are separated out into about 1000 ish records
column_names = ["Start", "Finish", "Count", "URL"]
df = pd.read_csv("URLs.csv", names = column_names)
all_pages = df.URL.to_list()
all_pages = all_pages[:] # Update whenever VPN gets blocked

page_count = 28
for pages in range(27, len(all_pages)):

    print("Scraping Page Number: " + str(page_count))
    page_count = page_count + 1
    
    # Go to the page to scrape
    print(all_pages[pages])
    driver.get(all_pages[pages])
    time.sleep(random.randint(10,12)/10)

    #Scroll to the bottom
    SCROLL_PAUSE_TIME = random.randint(19,21)/10
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Get all urls
    # /html/body/div[3]/div[4]/div/div/div[2]/div[2]/div[1]/div[1]/div/a
    # /html/body/div[3]/div[4]/div/div/div[2]/div[2]
    all_urls = driver.find_elements(By.XPATH, ".//div[@class='explorerPage__results--3wqLw']/div/div")
    one_url = all_urls[0]
    url = one_url.find_element(By.XPATH, "./div/a")
    all_str_urls = [url.find_element(By.XPATH, "./div/a").get_attribute('href') for url in all_urls]

    index = 1
    for url in all_str_urls:

        # Keep index documented
        print("Scraping Item Number: " + str(index))
        index = index + 1

        # Go into each link
        driver.get(url)
        
        # Clean dictionary to create the current row
        wine_dict = {}

        # Pull different elements using xpath
        try:
            #'.//span[@class="headline"]/a[@class="winery"]'
            winery = driver.find_element(By.XPATH, "//a[@class = 'anchor_anchor__m8Qi- breadCrumbs__link--1TY6b' and @data-cy='breadcrumb-winery']").text
            print(winery)
        except Exception as e:
            print(e)
            winery = 'NA'
            
        try:
            wine_type = driver.find_element(By.XPATH, ".//a[@class = 'anchor_anchor__m8Qi- breadCrumbs__link--1TY6b' and @data-cy='breadcrumb-grape']").text
            print(wine_type)
        except Exception as e:
            print(e)
            wine_type = 'NA'
            
        try:
            city = driver.find_element(By.XPATH, "//a[@class = 'anchor_anchor__m8Qi- breadCrumbs__link--1TY6b' and @data-cy='breadcrumb-region']").text
            print(city)
        except Exception as e:
            print(e)
            city = 'NA'
            
        try:
            country = driver.find_element(By.XPATH, "//a[@class = 'anchor_anchor__m8Qi- breadCrumbs__link--1TY6b' and @data-cy='breadcrumb-country']").text
            print(country)
        except Exception as e:
            print(e)
            country = 'NA'
            
        try:
            wine_name = driver.find_element(By.XPATH, './/span[@class="vintage"]/a[@class="wine"]').text
            print(wine_name)
        except Exception as e:
            print(e)
            wine_name = 'NA'
            
        try:
            year_prep = driver.find_element(By.XPATH, './/span[@class="vintage"]').text
            year = int(re.findall('\d+', year_prep)[-1])
            print(year)
        except Exception as e:
            print(e)
            year = -1
            
        try:
            overall_rating = float(driver.find_element(By.XPATH, './/div[@class="vivinoRating_averageValue__uDdPM"]').text)
            print(overall_rating)
        except Exception as e:
            print(e)
            overall_rating = -1
            
        try:
            overall_rating_count_prep = driver.find_element(By.XPATH, './/div[@class="vivinoRating_caption__xL84P"]').text
            overall_rating_count = int(re.findall('\d+', overall_rating_count_prep)[0])
            print(overall_rating_count)
        except Exception as e:
            print(e)
            overall_rating_count = -1
            
        try:
            time.sleep(random.randint(5,7)/10)
            price_prep = driver.find_element(By.XPATH, './/span[@class="purchaseAvailability__currentPrice--3mO4u"]').text
            price = float(re.findall('\d*\.?\d+', price_prep)[0])
            print(price)
        except:
            try:
                price_prep = driver.find_element(By.XPATH, './/span[@class="purchaseAvailabilityPPC__amount--2_4GT"]').text
                price = float(re.findall('\d*\.?\d+', price_prep)[0])
            except Exception as e:
                print(e)
                price = -1

        # Need some scrolling for the page to load
        try:
            driver.execute_script("window.scrollTo(0, 1080);")
            driver.execute_script("window.scrollTo(0, 1080);")
            driver.execute_script("window.scrollTo(0, 1080);")
            driver.execute_script("window.scrollTo(0, 1080);")
            driver.execute_script("window.scrollTo(0, 1080);")
            time.sleep(random.randint(20,22)/10)
            wine_dict = find_metrics(driver, wine_dict)
            print(wine_dict)
        except Exception as e:
            print(e)
            wine_dict['light_bold'] = -1
            wine_dict['smooth_tannic'] = -1
            wine_dict['dry_sweet'] = -1
            wine_dict['soft_acidic'] = -1

        # Define wine_dict and assign each element
        wine_dict['winery'] = winery
        wine_dict['wine_type'] = wine_type
        wine_dict['city'] = city
        wine_dict['country'] = country
        wine_dict['wine_name'] = wine_name
        wine_dict['year'] = year
        wine_dict['overall_rating'] = overall_rating
        wine_dict['overall_rating_count'] = overall_rating_count
        wine_dict['price'] = price

        try:
            writer.writerow(wine_dict)
        except Exception as e:
            print(e)
            pass
            
csv_file.close()