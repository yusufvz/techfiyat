# 1. Python'un resmi, hafif sürümünü temel al
FROM python:3.9-slim

# 2. Gerekli sistem araçlarını ve Chrome'u kur
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Çalışma klasörünü ayarla
WORKDIR /app

# 4. Gereksinim dosyasını kopyala ve kütüphaneleri kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Projenin geri kalanını kopyala
COPY . .

# 6. Portu dışarıya aç (Render genelde 10000 bekler ama biz Flask'a 5000 dedik, ayarlarız)
EXPOSE 5000

# 7. Uygulamayı başlat (Gunicorn ile)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]