# =========================================================================
# KAPLAN PARÇASI - REFLEX PRODUCTION DOCKERFILE
# =========================================================================

# 1. Aşama: Python 3.11 tabanlı kararlı ve hafif slim imajı kullanıyoruz
FROM python:3.11-slim

# Gerekli temel sistem paketlerini kuruyoruz (Reflex derlemesi için curl, unzip vb. şarttır)
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    gnupg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Node.js 18 ve npm kurulumunu gerçekleştiriyoruz (Reflex Next.js frontend derlemesi için zorunludur)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini /app olarak belirliyoruz
WORKDIR /app

# Önce bağımlılık listesini kopyalayıp pip önbelleğini kullanmadan temiz kurulum yapıyoruz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Geri kalan tüm proje dosyalarını container içerisine aktarıyoruz
COPY . .

# Eğer lokal sqlite/alembic veritabanı şemaları varsa ilklendiriyoruz
RUN reflex db init

# Üretim (Production) ortamı için frontend asset'lerini önceden derleyerek hazır hale getiriyoruz
# Bu adım Render üzerindeki "deploy timeout" veya derleme hatalarını tamamen engeller
RUN reflex export --frontend-only --no-zip

# Reflex servis portlarını dış dünyaya tanımlıyoruz
# Frontend varsayılan olarak 3000 portunu, Backend API ise 8000 portunu kullanır
EXPOSE 3000
EXPOSE 8000

# Uygulamayı üretim (production) profilinde çalıştırıyoruz
CMD ["reflex", "run", "--env", "prod"] 
