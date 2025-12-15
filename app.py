from flask import Flask

# DİKKAT: Botların hepsini kapattık. Import bile etmiyoruz.
# from hepsiburada import search_hepsiburada 

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Sistem Calisiyor!</h1><p>Sorun Selenium/Chrome kaynakliymis.</p>"

@app.route('/search')
def search():
    return "<h1>Arama Sayfasi</h1><p>Botlar su an devre disi.</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)