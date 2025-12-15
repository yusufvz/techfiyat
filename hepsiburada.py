from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

def search_hepsiburada(query):
    print(f"Hepsiburada taranıyor: {query}")
    results = []
    
    # Standart Render Ayarları (Bunlar Mecbur)
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    
    try:
        url = f"https://www.hepsiburada.com/ara?q={query.replace(' ', '+')}"
        driver.get(url)
        time.sleep(3) # Sayfanın yüklenmesi için 3 saniye bekle

        products = driver.find_elements(By.CSS_SELECTOR, "li[class*='productListContent']")
        
        # Sadece ilk 3 ürünü al (Hata riskini azaltır)
        for product in products[:3]:
            try:
                name = product.find_element(By.CSS_SELECTOR, "h3").text
                link = product.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                # Fiyatı metin içinden bul
                price_text = product.text
                matches = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?) ?TL', price_text)
                
                if matches:
                    # En mantıklı fiyatı al
                    prices = []
                    for m in matches:
                        clean = float(m.replace('.', '').replace(',', '.'))
                        if clean > 1000: # 1000 TL altını filtrele
                            prices.append(clean)
                    
                    if prices:
                        final_price = min(prices)
                        results.append({
                            "site": "Hepsiburada",
                            "name": name,
                            "price_str": f"{final_price:,.0f} TL".replace(',', '.'),
                            "price": final_price,
                            "link": link
                        })
            except:
                continue
    except Exception as e:
        print(f"HB Hata: {e}")
    finally:
        driver.quit()
        
    return results