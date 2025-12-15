from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

def search_n11(query):
    print(f"N11 taranıyor: {query}")
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
        url = f"https://www.n11.com/arama?q={query.replace(' ', '+')}"
        driver.get(url)
        time.sleep(3)

        products = driver.find_elements(By.CSS_SELECTOR, "li.column")
        
        for product in products[:3]:
            try:
                name = product.find_element(By.CSS_SELECTOR, "h3.productName").text
                link = product.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                price_text = product.text
                matches = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?) ?TL', price_text)
                
                if matches:
                    vals = []
                    for m in matches:
                        v = float(m.replace('.', '').replace(',', '.'))
                        if v > 1000: vals.append(v)
                    
                    if vals:
                        final = min(vals)
                        results.append({
                            "site": "N11",
                            "name": name,
                            "price_str": f"{final:,.0f} TL".replace(',', '.'),
                            "price": final,
                            "link": link
                        })
            except:
                continue
    except Exception as e:
        print(f"N11 Hata: {e}")
    finally:
        driver.quit()
        
    return results