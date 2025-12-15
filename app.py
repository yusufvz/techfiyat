from flask import Flask, render_template, request
import concurrent.futures
# Bot dosyalarımızı içeri aktarıyoruz
from hepsiburada import search_hepsiburada
from trendyol import search_trendyol
from n11 import search_n11
# from amazon import search_amazon  <-- Amazon'u şimdilik kapattık

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q')
    all_results = []
    
    # --- PARALEL İŞLEM MOTORU (3 SİTE) ---
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        
        # Görevleri aynı anda başlatıyoruz
        # 1. Hepsiburada
        futures.append(executor.submit(search_hepsiburada, query))
        
        # 2. Trendyol
        futures.append(executor.submit(search_trendyol, query))
        
        # 3. N11
        futures.append(executor.submit(search_n11, query))
        
        # Amazon'u işlemciyi yormamak için kapalı tutuyoruz
        # futures.append(executor.submit(search_amazon, query))

        # --- SONUÇLARI TOPLA ---
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                if data:
                    all_results.extend(data)
            except Exception as e:
                print(f"Site taramasında hata: {e}")

    # Tüm sonuçları fiyata göre sırala (En ucuz en üstte)
    all_results.sort(key=lambda x: x['price'])
    
    return render_template('results.html', results=all_results, query=query)

if __name__ == '__main__':
    # Threading modunu açıyoruz ki Flask da istekleri paralel karşılayabilsin
    app.run(host='0.0.0.0', port=5000, threaded=True)