from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from pprint import pprint
import time
import json

# Set up Chrome options
o = Options()
o.add_argument("start-maximized")

# Install and set up the Chrome driver
s=Service(ChromeDriverManager().install())

# Create a new instance of the Chrome driver with the specified options
browser = webdriver.Chrome(service=s, options=o)

# URL to be scraped
url = "https://www.fragrantica.com/search/?godina=2017%3A2017&country=United%20States"
browser.get(url)

for i in range(0,35):
    try:
        browser.find_element(By.XPATH,'//button[normalize-space()="Show more results"]').click()
        time.sleep(10)
    except Exception as e:
        print("An exception occurred:", e)
        break

html = browser.page_source
soup = bs(html, "html.parser")
browser.quit()

####### GET THE LENGTH OF THE RESULTS #######
# Get the list of perfume names
perfumeGrid = soup.find("span", class_="grid-x grid-margin-x grid-margin-y small-up-3 medium-up-2 large-up-4 perfumes-row text-center")
DictsList = []
Dict = {}
for str in perfumeGrid.find_all("a", href=True):
    perfumeName = str.get_text().replace('\n', '').strip(" ")
    perfumeURL= str['href']
    Dict = {"name": perfumeName,
            "url": perfumeURL
            }
    DictsList.append(Dict)

print(len(DictsList))
# Open a file in write mode and add the DictsList to it
with open('DictsList_2017.txt', 'w') as file:
    json.dump(DictsList, file)
time.sleep(3)