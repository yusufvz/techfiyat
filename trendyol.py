from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

def search_trendyol(query):
    print(f"Trendyol taranıyor: {query}")
    results = []
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    
    try:
        url = f"https://www.trendyol.com/sr?q={query.replace(' ', '%20')}"
        driver.get(url)
        time.sleep(3) # Yüklenmesini bekle

        products = driver.find_elements(By.CLASS_NAME, "p-card-wrppr")
        
        for product in products[:3]:
            try:
                brand = product.find_element(By.CLASS_NAME, "prdct-desc-cntnr-ttl").text
                name_part = product.find_element(By.CLASS_NAME, "prdct-desc-cntnr-name").text
                full_name = f"{brand} {name_part}"
                link = product.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                price_text = product.text
                # Basit fiyat bulucu
                match = re.search(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?) ?TL', price_text)
                
                if match:
                    clean = float(match.group(1).replace('.', '').replace(',', '.'))
                    if clean > 1000:
                        results.append({
                            "site": "Trendyol",
                            "name": full_name,
                            "price_str": f"{clean:,.0f} TL".replace(',', '.'),
                            "price": clean,
                            "link": link
                        })
            except:
                continue
    except Exception as e:
        print(f"TY Hata: {e}")
    finally:
        driver.quit()
        
    return results