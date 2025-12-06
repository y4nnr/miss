#!/bin/bash

# Script de configuration pour Miss France 2026

echo "🎯 Configuration de l'application Miss France 2026..."

# Créer l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Vérifier si la base de données existe
echo "🗄️  Vérification de la base de données..."
if ! psql -U postgres -lqt | cut -d \| -f 1 | grep -qw Miss; then
    echo "📊 Création de la base de données..."
    createdb -U postgres Miss
else
    echo "✅ La base de données existe déjà"
fi

# Initialiser les utilisateurs
echo "👥 Initialisation des utilisateurs..."
python init_db.py

# Scraper les candidates
echo "🌐 Scraping des candidates..."
python scraper.py

echo ""
echo "✅ Configuration terminée!"
echo ""
echo "Pour démarrer l'application:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""


