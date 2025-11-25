import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -------------------------
#  CLASE CHAMPION
# -------------------------
class Champion:
    def __init__(self, name, url, category, attackRange, movementSpeed, style, difficulty):
        self.name = name
        self.url = url
        self.category = category
        self.attackRange = attackRange
        self.movementSpeed = movementSpeed
        self.style = style
        self.difficulty = difficulty


# -------------------------
#  SCRAPER PRINCIPAL
# -------------------------
class ChampionScraper:

    baseURL = 'https://leagueoflegends.fandom.com'
    championsURL = "https://leagueoflegends.fandom.com/wiki/List_of_champions"

    def requestAndObtainParsedChampions(self):
        response = requests.get(self.championsURL, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        championsList = soup.find('table', {'class': 'sortable'}).find_all('tr')[1:]

        # 🟦 USO DEL DRIVER CON TU RUTA REAL
        service = Service(r"C:\webdrivers\chromedriver-win64\chromedriver.exe")
        driver = webdriver.Chrome(service=service)

        return map(lambda c: self.parseChampion(c, driver), championsList)

    def parseChampion(self, championSoup, driver):
        a_tags = championSoup.find_all('a')
        category = championSoup.find_all('td')[1]['data-sort-value'].lower()

        detailsURL = f"{self.baseURL}{a_tags[1]['href']}"

        return self.parseChampionDetails(category, detailsURL, driver)

    def parseChampionDetails(self, category, url, driver):
        driver.get(url)
        delay = 20

        WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.ID, 'flytabs_0-content-wrapper'))
        )

        page = BeautifulSoup(driver.page_source, "html.parser")

        # Datos del campeón
        name = page.find('h1', {'class': 'page-header__title'}).text.lower()

        tables = page.find_all('aside')
        stats = tables[1]
        general = tables[0]

        attackRange = stats.find('div', {'data-source': 'range'}).find('span').text
        movementSpeed = stats.find('div', {'data-source': 'ms'}).find('span').text

        style_raw = general.find('div', {'data-source': 'style'}).find_all('span')[1]['title']
        difficulty_raw = general.find('div', {'data-source': 'difficulty'}).find('div')['title']
        difficulty = re.findall('[0-9]+', difficulty_raw)[0]

        return Champion(
            name=name,
            url=url,
            category=category,
            attackRange=int(attackRange),
            movementSpeed=int(movementSpeed),
            style=int(style_raw),
            difficulty=int(difficulty)
        )


# -------------------------
#  FUNCIÓN USADA POR EL COG
# -------------------------
def load_champions():
    scraper = ChampionScraper()
    champions = []

    for c in scraper.requestAndObtainParsedChampions():
        champions.append({
            "name": c.name,
            "url": c.url,
            "category": c.category,
            "attackRange": c.attackRange,
            "movementSpeed": c.movementSpeed,
            "style": c.style,
            "difficulty": c.difficulty
        })

    return champions
