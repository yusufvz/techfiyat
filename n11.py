from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# --- EKLENEN KISIMLAR ---
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# ------------------------
import time
import re

def search_n11(query):
    print(f"🔍 N11'de aranıyor: {query}")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    
    # --- KRİTİK DÜZELTME ---
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"🚨 Sürücü Hatası: {e}")
        return []

    results = []

    try:
        search_url = f"https://www.n11.com/arama?q={query.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(3)
        driver.execute_script("window.scrollBy(0, 300);")
        
        cards = driver.find_elements(By.CSS_SELECTOR, "li.column")
        print(f"✅ N11: {len(cards)} ürün bulundu.")

        for card in cards[:5]:
            try:
                name = card.find_element(By.CSS_SELECTOR, "h3.productName").text
                link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                card_text = card.text
                matches = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?) ?TL', card_text)
                prices = []
                for m in matches:
                    try:
                        v = float(m.replace('.', '').replace(',', '.'))
                        if v > 2000: prices.append(v)
                    except: continue
                
                if prices:
                    final_price = min(prices)
                    results.append({
                        "site": "N11",
                        "name": name,
                        "price_str": f"{final_price:,.0f} TL".replace(',', '.'),
                        "price": final_price,
                        "link": link
                    })
            except: continue

    except Exception as e:
        print(f"🚨 N11 Hatası: {e}")
    finally:
        driver.quit()

    return results