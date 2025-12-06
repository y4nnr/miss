# Miss France 2026 - Application de Prédictions

Application web moderne et minimaliste pour prédire les résultats de Miss France 2026. Les utilisateurs peuvent se connecter et faire leurs prédictions pour les 3 premières places.

## Fonctionnalités

- 🔐 Authentification multi-utilisateurs
- 👑 Prédiction du top 3 (1ère, 2ème, 3ème place)
- 👥 30 candidates avec leurs informations
- 🎨 Interface moderne et minimaliste
- 📊 Visualisation des prédictions actuelles

## Prérequis

- Python 3.8+
- PostgreSQL (déjà en cours d'exécution)
- pip

## Installation

1. Créer un environnement virtuel (recommandé) :
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Créer la base de données PostgreSQL :
```bash
createdb -U postgres Miss
```

4. Initialiser la base de données avec les utilisateurs :
```bash
python init_db.py
```

5. Scraper et peupler les candidates :
```bash
python scraper.py
```

## Utilisation

1. Activer l'environnement virtuel (si vous l'utilisez) :
```bash
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

2. Démarrer l'application :
```bash
python app.py
```

2. Accéder à l'application :
Ouvrez votre navigateur à l'adresse : `http://localhost:5000`

3. Alternative - Utiliser le script de configuration automatique :
```bash
./setup.sh
```

3. Se connecter :
Utilisez l'un des comptes suivants (mot de passe = nom d'utilisateur) :
- fifi
- nono
- kiki
- keke
- yann
- baptiste
- steph
- renato
- benouz

## Structure du projet

```
miss/
├── app.py              # Application Flask principale
├── scraper.py          # Script de scraping des candidates
├── init_db.py          # Initialisation de la base de données
├── requirements.txt    # Dépendances Python
├── templates/          # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── predictions.html
│   └── candidates.html
└── static/
    └── css/
        └── style.css   # Styles CSS
```

## Base de données

L'application utilise PostgreSQL avec les tables suivantes :
- `user` : Utilisateurs de l'application
- `candidate` : Les 30 candidates à Miss France 2026
- `prediction` : Prédictions des utilisateurs

## Configuration

La connexion à la base de données est configurée dans `app.py` :
- Utilisateur : postgres
- Mot de passe : postgres
- Hôte : localhost
- Base de données : Miss

Pour modifier ces paramètres, éditez la ligne :
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/Miss'
```

