from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

def search_hepsiburada(query):
    print(f"🔍 Hepsiburada'da aranıyor: {query}")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    
    # --- KRİTİK DÜZELTME: Manager ile kurulum ---
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    results = []

    try:
        search_url = f"https://www.hepsiburada.com/ara?q={query.replace(' ', '+')}"
        driver.get(search_url)

        wait = WebDriverWait(driver, 15)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li[class*='productListContent']")))
        except:
            pass # Bulamazsa da devam etsin, hata vermesin
        
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(2)

        products = driver.find_elements(By.CSS_SELECTOR, "li[class*='productListContent']")
        print(f"✅ Hepsiburada: {len(products)} ürün bulundu.")

        for product in products[:5]: # RAM için limit 5
            try:
                name = ""
                try:
                    name = product.find_element(By.CSS_SELECTOR, "h3").text
                except:
                    continue

                try:
                    link = product.find_element(By.TAG_NAME, "a").get_attribute("href")
                except:
                    link = "#"

                # Fiyat okuma
                price_text = product.text
                matches = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?) ?TL', price_text)
                
                valid_prices = []
                for match in matches:
                    try:
                        clean = float(match.replace('.', '').replace(',', '.'))
                        if clean > 2000: valid_prices.append(clean)
                    except: continue

                if valid_prices:
                    final_price = min(valid_prices)
                    price_str = f"{final_price:,.0f} TL".replace(',', '.')
                    
                    results.append({
                        "site": "Hepsiburada",
                        "name": name,
                        "price_str": price_str,
                        "price": final_price,
                        "link": link
                    })
            except:
                continue

    except Exception as e:
        print(f"🚨 Hepsiburada Hatası: {e}")
    finally:
        driver.quit()

    return results