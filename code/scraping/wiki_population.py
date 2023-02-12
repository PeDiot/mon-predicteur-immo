"""Description. 
Retrieve census data for a given city from Wikipedia."""


# import
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import pandas as pd 

# selenium settings 
BACKUP_PATH = "../../data/densite/"
DRIVER_PATH = "C:/Users/pemma/AppData/Local/Programs/Python/Python39/chromedriver.exe"

URL = {
    "marseille": "https://fr.wikipedia.org/wiki/Secteurs_et_arrondissements_de_Marseille", 
    "lyon": "https://fr.wikipedia.org/wiki/Arrondissements_de_Lyon"
}

options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(DRIVER_PATH, options=options)

# choose your city 
city = "lyon"


# get data from wiki 
driver.get(URL[city])
html_code = driver.page_source
driver.close()


# process html code
soup = BeautifulSoup(html_code, "lxml")

table = soup.find(name="table", attrs={"class": "wikitable sortable jquery-tablesorter"})
body = table.find(name="tbody")
rows = body.find_all(name="tr")

# build dictionary to store data 
neighborhoods = {
    "code_commune": [], 
    "code_postal": [], 
    "nom_commune": [], 
    "pop": []
}

for ix, row in enumerate(rows): 
    items = row.find_all(name="td")

    neighborhoods["code_commune"].append(items[0].text)
    neighborhoods["code_postal"].append(items[1].text)
    neighborhoods["nom_commune"].append(items[2].find(name="a").get("title"))

    if city == "marseille" and ix % 2 != 0:
        pop_ix = 3
    else: 
        pop_ix = 4 
        
    neighborhoods["pop"].append(int(items[pop_ix].text.replace("\xa0", "")))

neighborhoods = pd.DataFrame(neighborhoods) 
print(neighborhoods)


# save final dataset 
file_path = BACKUP_PATH+"population_"+city+".csv"

neighborhoods.to_csv(file_path, index=False)
print(f"File saved at {file_path}.")