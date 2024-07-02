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
#o.add_argument("--headless")  # Run in headless mode

# Install and set up the Chrome driver
s=Service(ChromeDriverManager().install())

# Create a new instance of the Chrome driver with the specified options
browser = webdriver.Chrome(service=s, options=o)

# URL to be scraped
url = "https://www.fragrantica.com/perfume/Elizabeth-Arden/On-Dit-40559.html"
browser.get(url)

html = browser.page_source
soup = bs(html, "html.parser")

####### PULL FROM ORIGINAL NAME LIST #######
perfume_name = soup.find_all("div", class_="cell small-12")[3].find_all("b")[0].get_text()
perfume_comp = soup.find_all("div", class_="cell small-12")[3].find_all("b")[1].get_text()

perfume_image = soup.find_all("div", class_="cell small-12")[1].find("img")["src"]

######################get the gender##############
perfumeGender = soup.find("small").get_text()

######################get the rating##############
try:
    perfumeRating = float(soup.find("p", class_="info-note").find_all("span")[0].get_text())
except:
    perfumeRating = "Null"

######################get the Votes count#########
try:
    perfumeVotesCount = int(soup.find("p", class_="info-note").find_all("span")[2].get_text().replace(',', ''))
except:
    perfumeVotesCount = "Null"

# ##################find the description############  
# try:
#     perfumeDescription = soup.find_all("div", class_="cell small-12")[3].get_text().split('Read about this perfume')[0]
# except:
#     perfumeDescription = "Null"

####### MAIN ACCORDS DICTIONARY #######

try:
    main_accords = soup.find_all("div", class_="cell accord-box")
    accords_dict = {}
    for m in range(len(main_accords)):
        accord_name = main_accords[m].get_text()
        accord_value = float(main_accords[m].find("div", class_="accord-bar")["style"].rsplit("width: ")[1].strip("%;"))
        accords_dict[accord_name] = accord_value
except:
    accords_dict = {}
    print(f"{perfume_name} does not have accords")

####### FRAGRANCE NOTES #######        
notes = soup.find_all("div", attrs={"style": "display: flex; justify-content: center; text-align: center; flex-flow: wrap; align-items: flex-end; padding: 0.5rem;"})

if len(notes) == 3:
    number = 2
    top_notes_list = []
    middle_notes_list = []
    base_notes_list = []

    for n in range(len(notes[0].find_all("span", class_="link-span"))):
        top_notes_list.append(notes[0].find_all("div")[number].get_text())
        number += 3

    number = 2
    for p in range(len(notes[1].find_all("span", class_="link-span"))):
        middle_notes_list.append(notes[1].find_all("div")[number].get_text())
        number += 3

    number = 2
    for q in range(len(notes[2].find_all("span", class_="link-span"))):
        base_notes_list.append(notes[2].find_all("div")[number].get_text())
        number += 3
elif len(notes) == 2:
    number = 2
    top_notes_list = []
    middle_notes_list = []
    base_notes_list = []

    for r in range(len(notes[0].find_all("span", class_="link-span"))):
        top_notes_list.append(notes[0].find_all("div")[number].get_text())
        number += 3

    number = 2
    for s in range(len(notes[1].find_all("span", class_="link-span"))):
        middle_notes_list.append(notes[1].find_all("div")[number].get_text())
        number += 3
elif len(notes) == 1:
    number = 2
    top_notes_list = []
    middle_notes_list = []
    base_notes_list = []

    for v in range(len(notes[0].find_all("span", class_="link-span"))):
        middle_notes_list.append(notes[0].find_all("div")[number].get_text())
        number += 3
else:
    top_notes_list = []
    middle_notes_list = []
    base_notes_list = []

####### VOTING DATA & INFORMATION #######
voting = soup.find_all("div", class_="cell small-1 medium-1 large-1")

####### Longevity #######
long_v_weak = int(voting[0].get_text())
long_weak = int(voting[1].get_text())
long_moderate = int(voting[2].get_text())
long_long_last = int(voting[3].get_text())
long_eternal = int(voting[4].get_text())

####### Sillage #######
sill_intimate = int(voting[5].get_text())
sill_moderate = int(voting[6].get_text())
sill_strong = int(voting[7].get_text())
sill_enormus = int(voting[8].get_text())

####### Gender #######
gender_female = int(voting[9].get_text())
gender_more_fem = int(voting[10].get_text())
gender_unisex = int(voting[11].get_text())
gender_more_male = int(voting[12].get_text())
gender_male = int(voting[13].get_text())

####### Price Value #######
value_w_over = int(voting[14].get_text())
value_over = int(voting[15].get_text())
value_ok = int(voting[16].get_text())
value_good = int(voting[17].get_text())
value_great = int(voting[18].get_text())

####### CREATING THE DICTIONARY OF DATA #######
perfume_dict = {"name": perfume_name,
                "company": perfume_comp,
                "image": perfume_image,
                "for_gender": perfumeGender,
                "rating": perfumeRating,
                "number_votes": perfumeVotesCount,
                "main accords": accords_dict,
                #"description": perfumeDescription,
                "top notes": top_notes_list,
                "middle notes": middle_notes_list,
                "base notes": base_notes_list,
                "longevity":   {"very weak": long_v_weak,
                                "weak": long_weak,
                                "moderate": long_moderate,
                                "long lasting": long_long_last,
                                "eternal": long_eternal},
                "sillage":     {"intimate": sill_intimate,
                                "moderate": sill_moderate,
                                "strong": sill_strong,
                                "enormous": sill_enormus},
                "gender_vote": {"female": gender_female,
                                "more female": gender_more_fem,
                                "unisex": gender_unisex,
                                "more male": gender_more_male,
                                "male": gender_male},
                "price value": {"way overpriced": value_w_over,
                                "overpriced": value_over,
                                "ok": value_ok,
                                "good value": value_good,
                                "great value": value_great}
                }

time.sleep(2)

with open ("perfume_data_individual.txt", "w") as f:
    json.dump(perfume_dict, f)
browser.quit()
time.sleep(10)