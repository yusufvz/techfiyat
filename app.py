from flask import Flask, render_template, request
import concurrent.futures
# Bot dosyaları
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
    
    # --- AKILLI PARALEL MOD (MAX 2) ---
    # max_workers=2 diyerek RAM'i koruyoruz.
    # Aynı anda en fazla 2 site taranacak, biri bitince diğeri başlayacak.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        
        # Görevleri havuza atıyoruz
        futures.append(executor.submit(search_hepsiburada, query))
        futures.append(executor.submit(search_trendyol, query))
        futures.append(executor.submit(search_n11, query))
        
        # Sonuçları bekleyip topluyoruz
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                if data:
                    all_results.extend(data)
            except Exception as e:
                print(f"Bir site taranırken hata oluştu: {e}")

    # Fiyata göre sırala
    all_results.sort(key=lambda x: x['price'])
    
    return render_template('results.html', results=all_results, query=query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)