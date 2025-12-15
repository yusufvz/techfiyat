from flask import Flask, render_template, request
from hepsiburada import search_hepsiburada 
from trendyol import search_trendyol
from n11 import search_n11
from amazon import search_amazon
# Yeni veritabanı yöneticimizi çağırıyoruz
from db_manager import init_db, save_search_results, get_cached_results

app = Flask(__name__)

# Uygulama başlarken veritabanını bir kere kur
init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search():
    model = request.args.get("model")
    
    if not model:
        return render_template("index.html")

    # --- ADIM 1: ÖNCE HAFIZAYA BAK ---
    # 60 dakikadan daha yeni bir kayıt var mı?
    cached_data = get_cached_results(model, cache_duration_minutes=60)
    
    if cached_data:
        # EĞER VARSA: Hiç bot çalıştırma, direkt bunu göster!
        return render_template("result.html", model=model, fiyatlar=cached_data)

    # --- ADIM 2: HAFIZADA YOKSA BOTLARI ÇALIŞTIR ---
    print(f"\n🚀 Hafızada yok, siteler taranıyor: {model}")

    hb_results = search_hepsiburada(model)
    ty_results = search_trendyol(model)
    n11_results = search_n11(model)
    amz_results = search_amazon(model)

    # Hepsini birleştir
    all_results = hb_results + ty_results + n11_results + amz_results

    # Sırala
    all_results.sort(key=lambda x: x['price'])

    # --- ADIM 3: SONUÇLARI HAFIZAYA KAYDET ---
    if all_results:
        save_search_results(model, all_results)

    print(f"🏁 Toplam {len(all_results)} sonuç bulundu ve görüntülendi.\n")

    return render_template("result.html", model=model, fiyatlar=all_results)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)