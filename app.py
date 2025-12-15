from flask import Flask, render_template, request

# Hepsiburada dosyasını çağır (Trendyol ve N11 dosyaların duruyorsa onları da buraya ekleyebiliriz)
try:
    from hepsiburada import search_hepsiburada
except ImportError:
    search_hepsiburada = None

# Trendyol dosyan varsa yorumu kaldır
try:
    from trendyol import search_trendyol
except ImportError:
    search_trendyol = None

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q')
    all_results = []
    
    # --- 1. Hepsiburada Taraması ---
    if search_hepsiburada:
        try:
            print(">>> Hepsiburada Başlıyor...")
            hb_results = search_hepsiburada(query)
            if hb_results:
                all_results.extend(hb_results)
        except Exception as e:
            print(f"HB Hatası: {e}")

    # --- 2. Trendyol Taraması (Varsa çalışır) ---
    if search_trendyol:
        try:
            print(">>> Trendyol Başlıyor...")
            ty_results = search_trendyol(query)
            if ty_results:
                all_results.extend(ty_results)
        except Exception as e:
            print(f"TY Hatası: {e}")

    # Sonuçları Sırala
    all_results.sort(key=lambda x: x['price'])
    
    return render_template('results.html', results=all_results, query=query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)