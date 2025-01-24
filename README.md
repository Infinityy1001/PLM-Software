# PLM Software

![front-page](./assets/main.png)


0. Cloner le dépôt

```bash
git clone https://github.com/Infinityy1001/PLM-Software.git
```

```bash
cd PLM
```

1. Start a venv:

```bash 
python -m venv venv
```
Activate venv

```bash 
.\venv\Scripts\activate
```
Deactivate venv

```bash 
deactivate
```

2. Download requirements : 

```bash 
pip install -r requirements.txt
```

3. Launch the app 

```bash 
python run.py
```

4. Project Overview
```bash 
PLM/
│
├── venv/                   # Virtual environment
│
├── app/                    # Application directory
│   ├── __init__.py         # Initializes your Flask application
│   ├── config.py           # Configuration settings
│   ├── models.py           # Database models
│   ├── forms.py            # WTForms for form handling
│   ├── views/              # Application views and routes
│   │   ├── auth.py         # Authentication routes
│   │   ├── product.py      # Product management routes
│   │
│   ├── templates/          # HTML templates
│   │   ├── layout.html     # Base layout
│   │   ├── index.html      # Home page template
│   │   ├── login.html      # Login page template, etc.
│   │
│   ├── static/             # CSS, JavaScript files
│       ├── css/            # CSS files
│       ├── js/             # JavaScript files
│
├── run.py                  # Starts the Flask application
│
└── requirements.txt        # Python dependencies
```


Voici un exemple de fichier `README.md` que vous pouvez utiliser pour votre projet. Ce fichier fournit des instructions pour configurer l'environnement de développement, exécuter l'application, et connecter le projet à Git.

```markdown
# PLM - Product Lifecycle Management

Ce projet est une application Flask pour la gestion du cycle de vie des produits (PLM). Il inclut des fonctionnalités d'authentification, de gestion des produits, et une interface utilisateur basée sur des templates HTML.

## Structure du projet

```
PLM/
│
├── venv/                   # Environnement virtuel
│
├── app/                    # Répertoire de l'application
│   ├── __init__.py         # Initialisation de l'application Flask
│   ├── config.py           # Paramètres de configuration
│   ├── models.py           # Modèles de base de données
│   ├── forms.py            # WTForms pour la gestion des formulaires
│   ├── views/              # Vues et routes de l'application
│   │   ├── auth.py         # Routes d'authentification
│   │   ├── product.py      # Routes de gestion des produits
│   │
│   ├── templates/          # Templates HTML
│   │   ├── layout.html     # Layout de base
│   │   ├── index.html      # Template de la page d'accueil
│   │   ├── login.html      # Template de la page de connexion, etc.
│   │
│   ├── static/             # Fichiers CSS, JavaScript
│       ├── css/            # Fichiers CSS
│       ├── js/             # Fichiers JavaScript
│
├── run.py                  # Démarre l'application Flask
│
└── requirements.txt        # Dépendances Python
```

1. **Cloner le dépôt**

   ```bash
   git clone https://github.com/votre-utilisateur/PLM.git
   cd PLM
   ```

2. **Créer un environnement virtuel**

   ```bash
   python -m venv venv
   ```

3. **Activer l'environnement virtuel**

   - Sur Windows:

     ```bash
     venv\Scripts\activate
     ```

   - Sur macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

4. **Installer les dépendances**

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Configurer l'application**

   Modifiez le fichier `app/config.py` pour configurer les paramètres de l'application, tels que la clé secrète, la configuration de la base de données, etc.

2. **Initialiser la base de données**

   Si votre application utilise une base de données, vous pouvez l'initialiser en exécutant:

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

## Exécution de l'application

Pour démarrer l'application Flask, exécutez la commande suivante:

```bash
python run.py
```

L'application sera accessible à l'adresse `http://localhost:5000`.

## Connexion à Git

1. **Initialiser un dépôt Git**

   Si ce n'est pas déjà fait, initialisez un dépôt Git dans votre projet:

   ```bash
   git init
   ```

2. **Ajouter les fichiers au dépôt**

   ```bash
   git add .
   ```

3. **Faire un commit initial**

   ```bash
   git commit -m "Initial commit"
   ```

4. **Connecter le dépôt local à un dépôt distant**

   Si vous avez un dépôt distant sur GitHub ou autre, connectez-le:

   ```bash
   git remote add origin https://github.com/votre-utilisateur/PLM.git
   ```

5. **Pousser les changements**

   ```bash
   git push -u origin master
   ```

