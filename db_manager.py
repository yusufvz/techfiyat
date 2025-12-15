import sqlite3
import time

DB_NAME = "techfiyat.db"

def init_db():
    """Veritabanını ve tabloyu oluşturur (Eğer yoksa)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Sonuçları tutacak tablo
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_term TEXT,
            site TEXT,
            name TEXT,
            price_str TEXT,
            price REAL,
            link TEXT,
            timestamp REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_search_results(search_term, results):
    """Bulunan sonuçları veritabanına kaydeder"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Önce bu kelimeyle ilgili eski kayıtları temizleyelim (Üst üste binmesin)
    # search_term'i küçük harfe çevirip kaydediyoruz ki 'Asus' ile 'asus' aynı sayılsın
    term = search_term.lower().strip()
    cursor.execute("DELETE FROM results WHERE search_term = ?", (term,))
    
    current_time = time.time()
    
    for item in results:
        cursor.execute('''
            INSERT INTO results (search_term, site, name, price_str, price, link, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (term, item['site'], item['name'], item['price_str'], item['price'], item['link'], current_time))
        
    conn.commit()
    conn.close()
    print(f"💾 '{search_term}' için {len(results)} sonuç hafızaya kaydedildi.")

def get_cached_results(search_term, cache_duration_minutes=60):
    """Eğer hafızada taze veri varsa onu getirir, yoksa None döner"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    term = search_term.lower().strip()
    
    # Ne kadar eski veriyi kabul ediyoruz? (Varsayılan: 60 dakika)
    expiry_time = time.time() - (cache_duration_minutes * 60)
    
    # Hem kelime tutmalı HEM DE veri taze olmalı (timestamp > expiry_time)
    cursor.execute('''
        SELECT site, name, price_str, price, link FROM results 
        WHERE search_term = ? AND timestamp > ?
        ORDER BY price ASC
    ''', (term, expiry_time))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return None # Taze veri yok, botlar çalışmalı
    
    # Veritabanından gelen veriyi uygulamanın anlayacağı formata (liste) çeviriyoruz
    formatted_results = []
    for row in rows:
        formatted_results.append({
            "site": row[0],
            "name": row[1],
            "price_str": row[2],
            "price": row[3],
            "link": row[4]
        })
        
    print(f"📂 '{search_term}' için hafızadan {len(formatted_results)} sonuç yüklendi. (Bot çalışmadı!)")
    return formatted_results