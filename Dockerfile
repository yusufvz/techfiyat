# 1. Python'un hafif sürümünü kullan
FROM python:3.9-slim

# 2. Gerekli araçları yükle ve Chrome'u direkt indirip kur
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    ca-certificates \
    && wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Çalışma klasörünü ayarla
WORKDIR /app

# 4. Gereksinim dosyasını kopyala ve kütüphaneleri kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Projenin geri kalanını kopyala
COPY . .

# 6. Portu dışarıya aç
EXPOSE 5000

# 7. Uygulamayı başlat
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]