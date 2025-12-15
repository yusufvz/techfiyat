from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

def search_amazon(query):
    print(f"🔍 Amazon'da aranıyor: {query}")
    
    options = Options()
    # --- HIZ VE PERFORMANS AYARLARI ---
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
    # Amazon için ekstra dil ayarı (Bazen botu kandırmaya yarar)
    options.add_argument("accept-language=tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7")

    # Resimleri ve Bildirimleri Kapat
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
        
        # Sayfayı biraz aşağı kaydır (Ürünlerin yüklenmesi için)
        time.sleep(1)
        driver.execute_script("window.scrollBy(0, 600);")
        time.sleep(1)

        # Amazon ürün kartları
        product_cards = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
        print(f"✅ Amazon: Bulunan ürün sayısı: {len(product_cards)}")

        # İlk 5 ürünü al (Render limiti için sayıyı az tutuyoruz)
        for card in product_cards[:5]:
            try:
                # --- İSİM ---
                name = ""
                try:
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
                card_text = card.text
                valid_prices = []
                
                # Regex ile fiyatı metin içinden çek
                matches = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?)', card_text)
                
                for match in matches:
                    # Nokta ve virgül temizliği (12.500,00 -> 12500.0)
                    clean = match.replace('.', '').replace(',', '.')
                    try:
                        val = float(clean)
                        # Filtreleme: 10.000 TL altı ve 500.000 TL üstü mantıksız fiyatları ele
                        if val > 10000 and val < 500000:
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
        # Hata olsa bile botu çökertme, hatayı yaz ve boş liste dön
        print(f"🚨 Amazon Hatası: {e}")
    
    finally:
        driver.quit()

    return results