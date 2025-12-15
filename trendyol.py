from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

def search_trendyol(query):
    print(f"🔍 Trendyol'da aranıyor: {query}")
    results = []
    driver = None
    
    try:
        options = Options()
        # --- HIZ VE PERFORMANS AYARLARI (Render İçin Kritik) ---
        options.page_load_strategy = 'eager'  # Sayfanın tamamen bitmesini bekleme
        options.add_argument("--headless")    # Arka planda çalıştır
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions") 
        options.add_argument("--dns-prefetch-disable")
        options.add_argument("--window-size=1920,1080")
        
        # Bot olduğumuzu gizlemeye çalış
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
        
        # Resimleri Yükleme (Büyük Hız Kazandırır)
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        options.add_experimental_option("prefs", prefs)
        
        driver = webdriver.Chrome(options=options)

        # Arama URL'si
        url = f"https://www.trendyol.com/sr?q={query.replace(' ', '%20')}"
        driver.get(url)

        # Ürün kartlarının yüklenmesini bekle (Maksimum 10 saniye)
        wait = WebDriverWait(driver, 10)
        try:
            # Trendyol ürün kartı sınıfı
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "p-card-wrppr")))
        except:
            print("⚠️ Trendyol ürünleri yüklenemedi veya geç yanıt verdi.")
        
        # Hafif bir kaydırma yap (Lazy load tetiklensin diye)
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(1) # Kaydırma sonrası kısa bekleme

        # Ürünleri bul
        products = driver.find_elements(By.CLASS_NAME, "p-card-wrppr")
        print(f"✅ Trendyol: {len(products)} ürün bulundu.")

        # İLK 5 ÜRÜNÜ AL (Render'ı yormamak için limit koyduk)
        for product in products[:5]:
            try:
                # --- İSİM ÇEKME ---
                # Trendyol'da marka ve model ismi ayrı span'lardadır, birleştiriyoruz.
                try:
                    brand = product.find_element(By.CLASS_NAME, "prdct-desc-cntnr-ttl").text
                    name_part = product.find_element(By.CLASS_NAME, "prdct-desc-cntnr-name").text
                    full_name = f"{brand} {name_part}"
                except:
                    continue # İsmi alamazsak bu ürünü geç
                
                # --- LİNK ÇEKME ---
                try:
                    link_elem = product.find_element(By.TAG_NAME, "a")
                    link = link_elem.get_attribute("href")
                except:
                    link = "#"

                # --- FİYAT ÇEKME ---
                # İndirimli fiyatı almaya çalış, yoksa normal fiyatı al
                try:
                    price_text = product.find_element(By.CLASS_NAME, "prc-box-dscntd").text
                except:
                    try:
                        price_text = product.find_element(By.CLASS_NAME, "prc-box-sllng").text
                    except:
                        continue # Fiyat yoksa geç

                # Fiyat Temizleme (TL, nokta, virgül temizliği)
                # Örnek: "12.500 TL" -> 12500.0
                clean_price = price_text.replace('.', '').replace(',', '.').replace('TL', '').strip()
                match = re.search(r"(\d+(\.\d+)?)", clean_price)
                
                if match:
                    price_val = float(match.group(1))
                    
                    # Filtre: 2000 TL altı kılıf/aksesuardır, alma (Laptop arıyorsan)
                    if price_val > 2000:
                        results.append({
                            "site": "Trendyol",
                            "name": full_name,
                            "price_str": f"{price_val:,.0f} TL".replace(',', '.'), # Güzel görünen fiyat
                            "price": price_val, # Sıralama için sayısal fiyat
                            "link": link
                        })

            except Exception as e:
                # Tek bir üründe hata olursa döngüyü bozma, diğer ürüne geç
                continue

    except Exception as e:
        print(f"🚨 Trendyol Genel Hata: {e}")
    
    finally:
        if driver:
            driver.quit()
            
    return results