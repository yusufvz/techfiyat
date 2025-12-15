from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

def search_amazon(query):
    print(f"🔍 Amazon'da aranıyor: {query}")
    
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
        # Amazon TR Arama Linki
        search_url = f"https://www.amazon.com.tr/s?k={query.replace(' ', '+')}"
        driver.get(search_url)
        
        time.sleep(1)
        driver.execute_script("window.scrollBy(0, 600);")
        time.sleep(1)

        # Amazon ürün kartları: data-component-type="s-search-result"
        product_cards = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
        print(f"✅ Amazon: Bulunan ürün sayısı: {len(product_cards)}")

        for card in product_cards[:10]:
            try:
                # --- İSİM ---
                name = ""
                try:
                    # Amazon'da başlıklar genelde h2 içindeki span'dadır
                    name = card.find_element(By.TAG_NAME, "h2").text
                except:
                    continue

                # --- LİNK ---
                try:
                    link_elem = card.find_element(By.TAG_NAME, "h2").find_element(By.TAG_NAME, "a")
                    link = link_elem.get_attribute("href")
                except:
                    link = "#"

                # --- FİYAT ---
                # Amazon fiyatı bazen tam sayı ve kuruş olarak ayırır, metin taraması en iyisi
                card_text = card.text
                valid_prices = []
                
                # Amazon TR formatı: 34.999,00 TL veya sadece 34.999
                matches = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?)', card_text)
                
                for match in matches:
                    # Nokta ve virgül temizliği
                    clean = match.replace('.', '').replace(',', '.')
                    try:
                        val = float(clean)
                        # 10.000 TL üstü filtre
                        if val > 10000 and val < 500000: # Mantıksız yüksek sayıları da eleyelim
                            valid_prices.append(val)
                    except:
                        continue
                
                if valid_prices:
                    final_price = min(valid_prices)
                    price_str = f"{final_price:,.0f} TL".replace(',', '.')
                    
                    results.append({
                        "site": "Amazon",
                        "name": name,
                        "price_str": price_str,
                        "price": final_price,
                        "link": link
                    })

            except Exception:
                continue

    except Exception as e:
        print(f"🚨 Amazon Hatası: {e}")
    
    finally:
        driver.quit()

    return results