from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

def search_trendyol(query):
    print(f"\n🔍 Trendyol'da aranıyor: {query}")
    
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
        search_url = f"https://www.trendyol.com/sr?q={query.replace(' ', '+')}"
        driver.get(search_url)
        
        # Sayfanın yüklenmesi için statik bekleme
        time.sleep(1)
        
        # Sayfayı aşağı kaydır (Ürünlerin yüklenmesi için şart)
        print("📜 Sayfa kaydırılıyor...")
        driver.execute_script("window.scrollBy(0, 700);")
        time.sleep(1)
        driver.execute_script("window.scrollBy(0, 700);")
        time.sleep(1)

        # YÖNTEM: Sayfadaki TÜM linkleri (<a> etiketlerini) topla
        print("⏳ Linkler taranıyor...")
        all_links = driver.find_elements(By.TAG_NAME, "a")
        
        print(f"🔗 Sayfada toplam {len(all_links)} link bulundu.")

        # Sadece içinde ürün imzası ("-p-") olan linkleri filtrele
        product_links = []
        for link in all_links:
            href = link.get_attribute("href")
            if href and "-p-" in href and "sr?q=" not in href: # Arama linklerini hariç tut
                product_links.append(link)

        print(f"✅ Trendyol: Bulunan ÜRÜN sayısı: {len(product_links)}")

        # İlk 15 ürünü analiz et
        # (Set kullanarak aynı ürünü tekrar eklemeyi önleyelim)
        added_links = set()

        for link_element in product_links:
            if len(results) >= 10: break # 10 ürün yeterli

            try:
                href = link_element.get_attribute("href")
                if href in added_links: continue # Zaten eklediysek geç
                
                # Linkin içindeki metni (text) oku. Trendyol'da fiyat ve isim genelde linkin içindedir.
                card_text = link_element.text
                
                # Metin boşsa (bazen sadece resim olur), linkin kapsayıcı div'ine bak
                if not card_text.strip():
                    try:
                        # Linkin bir üst elementine (parent) bak
                        parent = link_element.find_element(By.XPATH, "./..")
                        card_text = parent.text
                    except:
                        pass

                # Eğer hala metin yoksa veya içinde TL yoksa geç
                if "TL" not in card_text:
                    continue

                # --- FİYAT BULMA ---
                valid_prices = []
                # Satır satır oku
                lines = card_text.split('\n')
                for line in lines:
                    if 'x' in line.lower() or 'taksit' in line.lower() or 'ay' in line.lower():
                        continue
                    
                    matches = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?) ?TL', line)
                    for match in matches:
                        clean = match.replace('.', '').replace(',', '.')
                        try:
                            val = float(clean)
                            if val > 10000: # Filtre
                                valid_prices.append(val)
                        except:
                            continue
                
                if not valid_prices: continue

                final_price = min(valid_prices)
                price_str = f"{final_price:,.0f} TL".replace(',', '.')

                # --- İSİM BULMA ---
                # Linkin içindeki en uzun metni isim olarak alalım
                name = ""
                longest_line = ""
                for line in lines:
                    if len(line) > len(longest_line) and "TL" not in line and "Kargo" not in line:
                        longest_line = line
                
                name = longest_line if len(longest_line) > 5 else "Trendyol Ürünü"

                print(f"   💰 {price_str} - {name[:30]}...")

                results.append({
                    "site": "Trendyol",
                    "name": name,
                    "price_str": price_str,
                    "price": final_price,
                    "link": href
                })
                
                added_links.add(href)

            except Exception:
                continue

    except Exception as e:
        print(f"🚨 Trendyol Hatası: {e}")
    
    finally:
        driver.quit()

    return results

if __name__ == "__main__":
    search_trendyol("asus tuf")