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
    # --- SUNUCU İÇİN ZORUNLU AYARLAR ---
    options.add_argument("--headless") # Sunucuda ekran olmadığı için ŞART
    options.add_argument("--no-sandbox") # Linux güvenliği için ŞART
    options.add_argument("--disable-dev-shm-usage") # Bellek hatası almamak için ŞART
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # --- İNSAN GİBİ GÖRÜNME AYARLARI ---
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    
    # Resimleri kapatma (Hız için)
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=options)
    results = []

    try:
        search_url = f"https://www.hepsiburada.com/ara?q={query.replace(' ', '+')}"
        driver.get(search_url)

        wait = WebDriverWait(driver, 15)
        print("⏳ Ürünlerin yüklenmesi bekleniyor...")
        
        # Ürün listesini bekle
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li[class*='productListContent']")))
        
        # Sayfayı biraz kaydır
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(2)

        products = driver.find_elements(By.CSS_SELECTOR, "li[class*='productListContent']")
        print(f"✅ Bulunan ham ürün sayısı: {len(products)}")

        for i, product in enumerate(products[:10]):
            try:
                # --- İSİM ---
                name = ""
                try:
                    name = product.find_element(By.CSS_SELECTOR, "h3").text
                except:
                    try:
                        name = product.find_element(By.TAG_NAME, "a").get_attribute("title")
                    except:
                        pass
                
                if not name:
                    continue

                # --- LİNK ---
                try:
                    link = product.find_element(By.TAG_NAME, "a").get_attribute("href")
                except:
                    link = "#"

                # --- AKILLI FİYAT BULMA (GELİŞMİŞ FİLTRE) ---
                # Kartın içindeki metni satır satır inceliyoruz
                card_text = product.text
                lines = card_text.split('\n') # Satırlara böl
                
                valid_prices = []

                for line in lines:
                    # EĞER SATIRDA "x" VARSA (Örn: 3 x 15.000) -> BU TAKSİTTİR, ATLA!
                    if ' x ' in line or 'taksit' in line.lower() or 'ay' in line.lower():
                        continue
                    
                    # Bu satırda "Rakam + TL" var mı?
                    matches = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?) ?TL', line)
                    
                    for match in matches:
                        clean = match.replace('.', '').replace(',', '.')
                        try:
                            val = float(clean)
                            # FİLTRE 1: 10.000 TL altı kupondur, at.
                            # FİLTRE 2: "x" içeren satırları zaten yukarıda eledik.
                            if val > 10000:
                                valid_prices.append(val)
                        except:
                            continue
                
                if valid_prices:
                    # Geçerli fiyatlar arasından en düşüğünü al (İndirimli fiyat)
                    final_price = min(valid_prices)
                    
                    # Formatla
                    price_str = f"{final_price:,.0f} TL".replace(',', '.')
                    
                    print(f"   💰 {name[:20]}... -> {price_str}") # Terminalde görelim

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
        print(f"🚨 Genel Hata: {e}")
    
    finally:
        driver.quit()

    # Fiyata göre sırala
    results.sort(key=lambda x: x['price'])
    return results

if __name__ == "__main__":
    veri = search_hepsiburada("asus tuf")
    print(f"\n✅ TOPLAM BAŞARILI: {len(veri)}")