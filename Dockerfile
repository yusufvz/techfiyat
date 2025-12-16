# 1. Python'un resmi, hafif sürümünü temel al
FROM python:3.9-slim

# 2. Gerekli sistem araçlarını kur
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    --no-install-recommends

# 3. Google Chrome'u doğrudan indir ve kur (En Garanti Yöntem)
# Repo anahtarlarıyla uğraşmadan direkt .deb dosyasını kuruyoruz.
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. Çalışma klasörünü ayarla
WORKDIR /app

# 5. Gereksinim dosyasını kopyala ve kütüphaneleri kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Projenin geri kalanını kopyala
COPY . .

# 7. Portu dışarıya aç
EXPOSE 5000

# 8. Uygulamayı başlat (Timeout süresini 120 saniye yaptık ki botlar rahat çalışsın)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "300", "app:app"]