# Utiliser une image Python officielle légère avec la version 3.11
FROM python:3.11-slim

# Empêcher Python de générer des fichiers .pyc et d'utiliser du buffer pour les logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système requises (si besoin pour certaines librairies Python)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de spécifications des paquets
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Exposer le port du serveur web
EXPOSE 8000

# Démarrer le serveur FastAPI avec Uvicorn
CMD ["uvicorn", "web:app", "--host", "0.0.0.0", "--port", "8000"]
