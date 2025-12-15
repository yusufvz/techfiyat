from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

def search_trendyol(query):
    print(f"🔍 Trendyol'da aranıyor: {query}")
    
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
    
    # --- KRİTİK DÜZELTME ---
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    results = []

    try:
        search_url = f"https://www.trendyol.com/sr?q={query.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(3)
        
        # Trendyol scroll sever
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(1)

        product_links = []
        all_links = driver.find_elements(By.TAG_NAME, "a")
        for link in all_links:
            href = link.get_attribute("href")
            if href and "-p-" in href and "sr?q=" not in href:
                product_links.append(link)

        print(f"✅ Trendyol: {len(product_links)} potansiyel ürün.")

        added_urls = set()
        for link_elem in product_links[:5]: # RAM için limit 5
            try:
                href = link_elem.get_attribute("href")
                if href in added_urls: continue
                
                card_text = link_elem.text
                if not card_text.strip(): # Yazı yoksa kapsayıcıya bak
                    try:
                        card_text = link_elem.find_element(By.XPATH, "./..").text
                    except: pass
                
                if "TL" not in card_text: continue

                matches = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?) ?TL', card_text)
                prices = []
                for m in matches:
                    try:
                        v = float(m.replace('.', '').replace(',', '.'))
                        if v > 2000: prices.append(v)
                    except: continue
                
                if not prices: continue
                
                final_price = min(prices)
                
                # İsim bulma (En uzun satırı isim varsayalım)
                lines = card_text.split('\n')
                name = "Trendyol Ürünü"
                longest = ""
                for line in lines:
                    if len(line) > len(longest) and "TL" not in line:
                        longest = line
                if len(longest) > 5: name = longest

                results.append({
                    "site": "Trendyol",
                    "name": name,
                    "price_str": f"{final_price:,.0f} TL".replace(',', '.'),
                    "price": final_price,
                    "link": href
                })
                added_urls.add(href)

            except: continue

    except Exception as e:
        print(f"🚨 Trendyol Hatası: {e}")
    finally:
        driver.quit()

    return results