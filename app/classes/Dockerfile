# Utiliser une image de base Python
FROM python:3.9-slim

# Mettre à jour les paquets système et installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Mettre à jour pip et installer les dépendances Python par étapes
RUN pip install --upgrade pip

# Installer les dépendances par lots pour minimiser les erreurs
RUN pip install --no-cache-dir psycopg2-binary>=2.9 numpy>=1.21.0 opencv-python>=4.5.1
RUN pip install --no-cache-dir face_recognition>=1.3.0 pandas>=1.3.0 fpdf>=1.7.2
RUN pip install --no-cache-dir matplotlib>=3.4.0 imapclient>=2.2.0 PyQt5>=5.15.0 Pillow>=8.2.0

# Configurer un point d'entrée
WORKDIR /app/classes
COPY . /app/classes

# Commande par défaut pour le conteneur
CMD ["python", "Menu.py"]
