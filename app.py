from flask import Flask, render_template, request
# Bot dosyalarımız
from hepsiburada import search_hepsiburada
from trendyol import search_trendyol
from n11 import search_n11

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q')
    all_results = []
    
    # --- GÜVENLİ SIRALI MOD ---
    # Siteleri tek tek tarayacağız ki RAM şişmesin.
    
    # 1. Hepsiburada
    try:
        print("Hepsiburada taranıyor...")
        hb_data = search_hepsiburada(query)
        if hb_data:
            all_results.extend(hb_data)
    except Exception as e:
        print(f"Hepsiburada hatası: {e}")

    # 2. Trendyol
    try:
        print("Trendyol taranıyor...")
        ty_data = search_trendyol(query)
        if ty_data:
            all_results.extend(ty_data)
    except Exception as e:
        print(f"Trendyol hatası: {e}")

    # 3. N11
    try:
        print("N11 taranıyor...")
        n11_data = search_n11(query)
        if n11_data:
            all_results.extend(n11_data)
    except Exception as e:
        print(f"N11 hatası: {e}")

    # Sonuçları fiyata göre sırala
    all_results.sort(key=lambda x: x['price'])
    
    return render_template('results.html', results=all_results, query=query)

if __name__ == '__main__':
    # Threaded=False yaparak hafızayı daha da koruyabiliriz
    app.run(host='0.0.0.0', port=5000)