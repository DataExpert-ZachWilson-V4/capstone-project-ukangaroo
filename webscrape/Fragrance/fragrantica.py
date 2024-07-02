from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from pprint import pprint
import time
import json

#instantiate the browser driver
s=Service(ChromeDriverManager().install())
o=Options()
o.add_argument("start-maximized")
driver = webdriver.Chrome(service=s, options=o)

#Search URL with UAE as a filter
url = "https://www.fragrantica.com/search/?country=United%20States"
driver.get(url)
time.sleep(10)

# click load more results to load more perfume details
for i in range(0,10):
    try:
        driver.find_element(By.XPATH,'//button[normalize-space()="Show more results"]').click()
        time.sleep(10)
    except Exception as e:
        print("An exception occurred:", e)
        break

# Get the page html 
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

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

# Open a file in write mode and add the DictsList to it
with open('DictsList.txt', 'w') as file:
    json.dump(DictsList, file)
time.sleep(3)
driver.quit()

# # printing 1st perfume details to see structre
# pprint(DictsList[0])

# #printing count of loaded perfumes
# DictsList = []
# with open('DictsList.txt', 'r') as file:
#     DictsList= json.load(file)
# print(len(DictsList))

#Get in each perfume's page to get the it's details
perfumesDictsList=[]
for i in range(len(DictsList)):#update this later len(DictsList)
    try:
        driver = webdriver.Chrome(service=s, options=o)
        driver.get(DictsList[i]["url"])
        time.sleep(10)
    except:
        break
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
###################get the URL####################
    perfumeUrl=DictsList[i]["url"]

################get the Name######################
    perfumeName = soup.find_all("div", class_="cell small-12")[3].find_all("b")[0].get_text()

################get the designer##################
    perfumeDesigner = soup.find_all("div", class_="cell small-12")[3].find_all("b")[1].get_text()

######################get the img#################
    perfumeImage = soup.find_all("div", class_="cell small-12")[1].find("img")["src"]

######################get the gender##############
    perfumeGender = soup.find("small").get_text()
    try:
        perfumeRating = float(soup.find("p", class_="info-note").find_all("span")[0].get_text())
    except:
        perfumeRating = "Null"

######################get the Votes count#########
    try:
        perfumeVotesCount = int(soup.find("p", class_="info-note").find_all("span")[2].get_text().replace(',', ''))
    except:
        perfumeVotesCount = "Null"

##################find the description############
    try:
        perumeDescription = soup.find_all("div", class_="cell small-12")[3].get_text().split('Read about this perfume')[0]
    except:
        perumeDescription = "Null"

##################find the accords###############
    try:
        perfumeAccords = soup.find_all("div", class_="cell accord-box")
        perfumeAccordsDict = {}
        for i in range(len(perfumeAccords)):
            accordName = perfumeAccords[i].get_text()
            accordValue = float(perfumeAccords[i].find("div", class_="accord-bar")["style"].rsplit("width: ")[1].strip("%;"))
            perfumeAccordsDict[accordName] = accordValue
    except:
            perfumeAccordsDict = {}

#################find the notes#################
    perfumeNotes = soup.find_all("div", attrs={"style": "display: flex; justify-content: center; text-align: center; flex-flow: wrap; align-items: flex-end; padding: 0.5rem;"})
    if len(perfumeNotes) == 3:
        i = 2
        perfumeTopNotes = []
        perfumeMidNotes = []
        perfumeBaseNotes = []
        for j in range(len(perfumeNotes[0].find_all("span", class_="link-span"))):
            perfumeTopNotes.append(perfumeNotes[0].find_all("div")[i].get_text())
            i += 3
        i = 2
        for j in range(len(perfumeNotes[1].find_all("span", class_="link-span"))):
            perfumeMidNotes.append(perfumeNotes[1].find_all("div")[i].get_text())
            i += 3
        i = 2
        for j in range(len(perfumeNotes[2].find_all("span", class_="link-span"))):
            perfumeBaseNotes.append(perfumeNotes[2].find_all("div")[i].get_text())
            i += 3
    elif len(perfumeNotes) == 2:
        i = 2
        perfumeTopNotes = []
        perfumeMidNotes = []
        perfumeBaseNotes = []
        for j in range(len(perfumeNotes[0].find_all("span", class_="link-span"))):
            perfumeTopNotes.append(perfumeNotes[0].find_all("div")[i].get_text())
            i += 3
        i = 2
        for j in range(len(perfumeNotes[1].find_all("span", class_="link-span"))):
            perfumeMidNotes.append(perfumeNotes[1].find_all("div")[i].get_text())
            i += 3              
    elif len(perfumeNotes) == 1:
        i = 2
        perfumeTopNotes = []
        perfumeMidNotes = []
        perfumeBaseNotes = []
        for j in range(len(perfumeNotes[0].find_all("span", class_="link-span"))):
            perfumeMidNotes.append(perfumeNotes[0].find_all("div")[i].get_text())
            i += 3      
    else:
        perfumeTopNotes = []
        perfumeMidNotes = []
        perfumeBaseNotes = []

#################find the Max voting#################
    voting = soup.find_all("div", class_="cell small-1 medium-1 large-1")
    # Define dictionaries to map index to label for each category
    labels = {
    "Longevity": {0: "very weak", 1: "weak", 2: "moderate", 3: "long lasting", 4: "eternal"},
    "Sillage": {0: "intimate", 1: "moderate", 2: "strong", 3: "enormous"},
    "Gender": {0: "female", 1: "more female", 2: "unisex", 3: "more male", 4: "male"},
    "PriceValue": {0: "way over", 1: "over", 2: "ok", 3: "good", 4: "great"}
    }
    maxLabels = {}
    # Iterate over each category
    for category, labelMap in labels.items():
        # Find the index of the maximum value in the voting list for the current category
        maxIndex = max(range(len(labelMap)), key=lambda i: int(voting[i].get_text()))
        # Retrieve the corresponding label from the label map
        maxLabel = labelMap[maxIndex]
        # Store the category and its corresponding label with maximum votes in the maxLabels dictionary
        maxLabels[category] = maxLabel

############prepare the json and write it to the file###############
# creating each perfume's data in a json object
    perfumeDict = {
                "url": perfumeUrl,
                "name": perfumeName,
                "desiger": perfumeDesigner,
                "image": perfumeImage,
                "gender": perfumeGender,
                "rating": perfumeRating,
                "votes count": perfumeVotesCount,
                "description": perumeDescription,
                "accords": perfumeAccordsDict,
                "top notes": perfumeTopNotes,
                "mid notes": perfumeMidNotes,
                "base notes": perfumeBaseNotes,
                "max votes": maxLabels
            }
    perfumesDictsList.append(perfumeDict)
# writing a copy of the perfume object to the json file
    with open('perfumesDictsList.txt', 'w') as file:
        json.dump(perfumesDictsList, file)
    driver.quit()
    time.sleep(10)

# # printing 1st perfume details to see structure
# pprint(perfumesDictsList[0])