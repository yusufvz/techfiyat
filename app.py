from flask import Flask, render_template, request
# Sadece çalışan 3'lüyü alıyoruz
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
    
    # --- 1. Hepsiburada ---
    print("Hepsiburada taranıyor...")
    try:
        hb_data = search_hepsiburada(query)
        if hb_data:
            all_results.extend(hb_data)
    except:
        pass # Hata olursa görmezden gel, sistemi bozma

    # --- 2. Trendyol ---
    print("Trendyol taranıyor...")
    try:
        ty_data = search_trendyol(query)
        if ty_data:
            all_results.extend(ty_data)
    except:
        pass

    # --- 3. N11 ---
    print("N11 taranıyor...")
    try:
        n11_data = search_n11(query)
        if n11_data:
            all_results.extend(n11_data)
    except:
        pass

    # Fiyata göre sırala
    if all_results:
        all_results.sort(key=lambda x: x['price'])
    
    return render_template('results.html', results=all_results, query=query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)