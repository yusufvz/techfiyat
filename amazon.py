from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

def search_amazon(query):
    print(f"🔍 Amazon'da aranıyor: {query}")
    
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
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    results = []

    try:
        search_url = f"https://www.amazon.com.tr/s?k={query.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(3)
        
        cards = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
        print(f"✅ Amazon: {len(cards)} ürün bulundu.")

        for card in cards[:5]: # RAM için limit 5
            try:
                try:
                    name = card.find_element(By.TAG_NAME, "h2").text
                except: continue

                try:
                    link = card.find_element(By.TAG_NAME, "h2").find_element(By.TAG_NAME, "a").get_attribute("href")
                except: link = "#"
                
                card_text = card.text
                matches = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?)', card_text)
                
                prices = []
                for m in matches:
                    clean = m.replace('.', '').replace(',', '.')
                    try:
                        v = float(clean)
                        if v > 2000 and v < 500000: prices.append(v)
                    except: continue
                
                if prices:
                    final_price = min(prices)
                    results.append({
                        "site": "Amazon",
                        "name": name,
                        "price_str": f"{final_price:,.0f} TL".replace(',', '.'),
                        "price": final_price,
                        "link": link
                    })
            except: continue

    except Exception as e:
        print(f"🚨 Amazon Hatası: {e}")
    finally:
        driver.quit()

    return results