from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re


class SingleChampionScraper:

    baseURL = "https://leagueoflegends.fandom.com/wiki/"

    def __init__(self):
        # Configurar Chrome en modo headless
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)

    def get_champion(self, champion_name: str):
        try:
            formatted = champion_name.replace(" ", "_")
            url = f"{self.baseURL}{formatted}/LoL"

            self.driver.get(url)
            
            # Esperar a que el infobox cargue
            wait = WebDriverWait(self.driver, 10)
            infobox = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "portable-infobox"))
            )

            # Obtener el nombre
            try:
                name_element = self.driver.find_element(By.CLASS_NAME, "pi-title")
                name = name_element.text.strip()
            except:
                name = formatted

            # Función para extraer stats
            def parse_stat(label_text):
                try:
                    labels = infobox.find_elements(By.CLASS_NAME, "pi-data-label")
                    for label in labels:
                        if label_text.lower() in label.text.strip().lower():
                            parent = label.find_element(By.XPATH, "..")
                            value_div = parent.find_element(By.CLASS_NAME, "pi-data-value")
                            text = value_div.text.strip()
                            
                            # Parsear "669 + 106" o similar
                            match = re.search(r'(\d+\.?\d*)\s*[\(\+]\s*(\d+\.?\d*)', text)
                            if match:
                                return match.group(1), match.group(2)
                            
                            # Solo valor base
                            match = re.search(r'(\d+\.?\d*)', text)
                            if match:
                                return match.group(1), "N/A"
                except:
                    pass
                return "N/A", "N/A"

            def parse_single(label_text):
                try:
                    labels = infobox.find_elements(By.CLASS_NAME, "pi-data-label")
                    for label in labels:
                        if label_text.lower() in label.text.strip().lower():
                            parent = label.find_element(By.XPATH, "..")
                            value_div = parent.find_element(By.CLASS_NAME, "pi-data-value")
                            text = value_div.text.strip()
                            match = re.search(r'(\d+\.?\d*)', text)
                            if match:
                                return match.group(1)
                except:
                    pass
                return "N/A"

            hp_base, hp_plus = parse_stat("health")
            mp_base, mp_plus = parse_stat("resource")
            armor_base, armor_plus = parse_stat("armor")
            ad_base, ad_plus = parse_stat("attack damage")

            stats = {
                "hp": hp_base,
                "hp_plus": hp_plus,
                "mp": mp_base,
                "mp_plus": mp_plus,
                "armor": armor_base,
                "armor_plus": armor_plus,
                "ad": ad_base,
                "ad_plus": ad_plus,
                "as": parse_single("attack speed"),
                "movespeed": parse_single("move speed")
            }

            return {
                "name": name,
                "url": url,
                "stats": stats
            }

        except Exception as e:
            print(f"Error scraping {champion_name}: {str(e)}")
            return None

    def close(self):
        """Cerrar el navegador cuando termines"""
        self.driver.quit()
