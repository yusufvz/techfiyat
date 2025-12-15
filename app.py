from flask import Flask, render_template, request

# --- BOTLARI GÜVENLİ ŞEKİLDE İÇERİ AL ---
try:
    from hepsiburada import search_hepsiburada
except ImportError:
    search_hepsiburada = None
    print("UYARI: hepsiburada.py dosyası bulunamadı.")

try:
    from trendyol import search_trendyol
except ImportError:
    search_trendyol = None
    print("UYARI: trendyol.py dosyası bulunamadı.")

try:
    from n11 import search_n11
except ImportError:
    search_n11 = None
    print("UYARI: n11.py dosyası bulunamadı.")

try:
    from amazon import search_amazon
except ImportError:
    search_amazon = None
    print("UYARI: amazon.py dosyası bulunamadı.")


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q')
    all_results = []
    errors = []
    
    # --- 1. HEPSIBURADA ---
    if search_hepsiburada:
        try:
            print(">>> Hepsiburada taranıyor...")
            hb_data = search_hepsiburada(query)
            if hb_data: all_results.extend(hb_data)
        except Exception as e:
            err_msg = f"Hepsiburada Hatası: {str(e)}"
            print(err_msg)
            errors.append(err_msg)
    
    # --- 2. TRENDYOL ---
    if search_trendyol:
        try:
            print(">>> Trendyol taranıyor...")
            ty_data = search_trendyol(query)
            if ty_data: all_results.extend(ty_data)
        except Exception as e:
            err_msg = f"Trendyol Hatası: {str(e)}"
            print(err_msg)
            errors.append(err_msg)

    # --- 3. N11 ---
    if search_n11:
        try:
            print(">>> N11 taranıyor...")
            n11_data = search_n11(query)
            if n11_data: all_results.extend(n11_data)
        except Exception as e:
            err_msg = f"N11 Hatası: {str(e)}"
            print(err_msg)
            errors.append(err_msg)

    # --- 4. AMAZON ---
    if search_amazon:
        try:
            print(">>> Amazon taranıyor...")
            amz_data = search_amazon(query)
            if amz_data: all_results.extend(amz_data)
        except Exception as e:
            # Amazon çok korumalı olduğu için hata çıkması normaldir
            err_msg = f"Amazon Hatası: {str(e)}"
            print(err_msg)
            errors.append(err_msg)

    # Sonuçları fiyata göre sırala (En ucuz en üstte)
    all_results.sort(key=lambda x: x['price'])
    
    # Hiçbir siteden sonuç gelmezse ve hatalar varsa ekrana bas
    if not all_results and errors:
        return f"<h1>Sonuç Bulunamadı :(</h1><h3>Hata Raporu:</h3><pre>{'<br>'.join(errors)}</pre>"
    
    return render_template('results.html', results=all_results, query=query)

if __name__ == '__main__':
    # Threaded=False yaparak RAM kullanımını minimumda tutuyoruz
    app.run(host='0.0.0.0', port=5000, threaded=False)