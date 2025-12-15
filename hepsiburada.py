from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

def search_hepsiburada(query):
    print(f"🔍 Hepsiburada'da aranıyor: {query}")
    
    options = Options()
    # --- HIZ VE PERFORMANS AYARLARI ---
    options.page_load_strategy = 'eager'  # <--- SİHİRLİ KOD BU! (Sayfanın bitmesini beklemez)
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions") # Eklentileri kapat
    options.add_argument("--dns-prefetch-disable") # DNS aramalarını bekleme
    options.add_argument("--window-size=1920,1080")
    
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    
    # Resimleri tamamen engelle
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2
    }
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=options)
    results = []

    try:
        search_url = f"https://www.hepsiburada.com/ara?q={query.replace(' ', '+')}"
        driver.get(search_url)

        # Bekleme süresini azalttık (Sadece ürün listesi görünene kadar bekle)
        wait = WebDriverWait(driver, 10)
        
        try:
            # Ürün listesini bekle
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li[class*='productListContent']")))
        except:
            print("⚠️ Ürün listesi geç yüklendi veya bulunamadı.")

        # Kaydırma işlemini azalttık
        driver.execute_script("window.scrollBy(0, 200);")
        time.sleep(1) # Sadece 1 saniye bekle

        products = driver.find_elements(By.CSS_SELECTOR, "li[class*='productListContent']")
        print(f"✅ Bulunan ham ürün sayısı: {len(products)}")

        # İlk 5 ürünü al (Hız için sayıyı düşürdük, istersen artırabilirsin)
        for i, product in enumerate(products[:5]):
            try:
                # --- İSİM ---
                name = ""
                try:
                    name = product.find_element(By.CSS_SELECTOR, "h3").text
                except:
                    continue # İsmi olmayan ürünü atla, vakit kaybetme
                
                if not name: continue

                # --- LİNK ---
                try:
                    link = product.find_element(By.TAG_NAME, "a").get_attribute("href")
                except:
                    link = "#"

                # --- FİYAT ---
                # Text işlemleri hızlıdır, burada yavaşlama olmaz
                card_text = product.text
                lines = card_text.split('\n')
                valid_prices = []

                for line in lines:
                    if ' x ' in line or 'taksit' in line.lower() or 'ay' in line.lower():
                        continue
                    
                    matches = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?) ?TL', line)
                    for match in matches:
                        clean = match.replace('.', '').replace(',', '.')
                        try:
                            val = float(clean)
                            if val > 10000:
                                valid_prices.append(val)
                        except:
                            continue
                
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

            except Exception:
                continue

    except Exception as e:
        print(f"🚨 Hata: {e}")
    
    finally:
        driver.quit()

    results.sort(key=lambda x: x['price'])
    return results