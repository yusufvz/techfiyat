from flask import Flask, render_template, request

# Diğerlerini bilerek kapattık, hata varsa onlardan gelmesin.
try:
    from hepsiburada import search_hepsiburada
except ImportError:
    search_hepsiburada = None
    print("HATA: hepsiburada.py dosyası bulunamadı!")

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q')
    all_results = []
    
    # --- SADECE HEPSIBURADA ---
    # Eğer bu çalışırsa sunucun sağlam demektir.
    if search_hepsiburada:
        try:
            print("Hepsiburada taranıyor...")
            results = search_hepsiburada(query)
            if results:
                all_results.extend(results)
        except Exception as e:
            print(f"Hepsiburada Hatası: {e}")
            # Hatayı ekrana basalım ki ne olduğunu görelim
            return f"<h1>Hepsiburada Hatası:</h1><p>{e}</p>"

    return render_template('results.html', results=all_results, query=query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)