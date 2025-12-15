from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

def search_n11(query):
    print(f"🔍 N11'de aranıyor: {query}")
    
    options = Options()
    # --- HIZ VE PERFORMANS AYARLARI (TÜM SİTELER İÇİN) ---
    options.page_load_strategy = 'eager'  # Sayfanın tamamen bitmesini bekleme
    options.add_argument("--headless")    # Ekran yok (Hız artar)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions") 
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--window-size=1920,1080")
    
    # Bot olduğumuzu gizle
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    
    # Resimleri ve Bildirimleri Kapat (Büyük Hız Kazandırır)
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2
    }
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=options)
    results = []

    try:
        # N11 Arama Linki
        search_url = f"https://www.n11.com/arama?q={query.replace(' ', '+')}"
        driver.get(search_url)
        
        time.sleep(1)
        
        # Sayfayı kaydır
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(1)

        # N11'de ürünler genelde "li.column" içindedir
        product_cards = driver.find_elements(By.CSS_SELECTOR, "li.column")
        print(f"✅ N11: Bulunan ürün sayısı: {len(product_cards)}")

        for card in product_cards[:10]:
            try:
                card_text = card.text
                
                # --- İSİM BULMA ---
                name = ""
                try:
                    name = card.find_element(By.CSS_SELECTOR, "h3.productName").text
                except:
                    continue # İsmi yoksa geç

                # --- LİNK BULMA ---
                try:
                    link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                except:
                    link = "#"

                # --- FİYAT BULMA ---
                valid_prices = []
                lines = card_text.split('\n')
                
                for line in lines:
                    # N11 bazen "Kazananlar Kulübü" gibi metinler ekler, elemeye gerek yok regex halleder
                    matches = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?) ?TL', line)
                    for match in matches:
                        clean = match.replace('.', '').replace(',', '.')
                        try:
                            val = float(clean)
                            if val > 10000: # 10.000 TL altı filtre
                                valid_prices.append(val)
                        except:
                            continue
                
                if valid_prices:
                    final_price = min(valid_prices)
                    price_str = f"{final_price:,.0f} TL".replace(',', '.')
                    
                    results.append({
                        "site": "N11",
                        "name": name,
                        "price_str": price_str,
                        "price": final_price,
                        "link": link
                    })

            except Exception:
                continue

    except Exception as e:
        print(f"🚨 N11 Hatası: {e}")
    
    finally:
        driver.quit()

    return results