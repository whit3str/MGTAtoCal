# MTG Release Tracker

Un ensemble d'outils pour suivre les prochaines sorties de Magic: The Gathering, télécharger automatiquement les fonds d'écran officiels et créer des événements dans Google Calendar.

## Présentation

Ce projet contient trois scripts Python qui fonctionnent ensemble pour :

1. **CODEDumper.py** - Récupérer les informations sur les prochaines sorties de sets Magic: The Gathering via l'API Scryfall
2. **WPDumper.py** - Télécharger automatiquement les fonds d'écran (wallpapers) officiels des prochaines extensions
3. **CODEtoGCal.py** - Créer des événements dans Google Calendar pour les dates de sortie

## Prérequis

- Python 3.6 ou plus récent
- Les bibliothèques Python listées dans `requirements.txt`
- Un compte Google et des identifiants OAuth pour l'API Google Calendar

## Installation

1. Clonez ce dépôt ou téléchargez les fichiers
2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

3. Pour l'intégration avec Google Calendar, vous devez :
   - Créer un projet dans la [Console Google Cloud](https://console.cloud.google.com/)
   - Activer l'API Google Calendar
   - Créer des identifiants OAuth et télécharger le fichier `credentials.json`
   - Placer le fichier `credentials.json` à la racine du projet

## Configuration

Les fichiers suivants sont utilisés pour la configuration :

- **upcoming_magic_sets.csv** - Contient les informations sur les prochains sets Magic (généré par CODEDumper.py)
- **credentials.json** - Identifiants OAuth pour l'API Google Calendar (à fournir par l'utilisateur)
- **token.pickle** - Token d'authentification pour Google Calendar (généré automatiquement)

## Utilisation

### 1. Récupérer les informations sur les prochains sets

```bash
python CODEDumper.py
```

Ce script :
- Récupère les données des sets Magic via l'API Scryfall
- Filtre les sets pour exclure certains types (commander, promo, etc.)
- Sélectionne les 10 prochains sets à sortir
- Génère le fichier `upcoming_magic_sets.csv`

### 2. Télécharger les fonds d'écran

```bash
python WPDumper.py
```

Ce script :
- Lit le fichier `upcoming_magic_sets.csv`
- Tente de télécharger les fonds d'écran officiels pour chaque set
- Extrait et renomme les fonds d'écran en résolution 1920x1080
- Les sauvegarde dans le dossier `resources/`

### 3. Créer des événements dans Google Calendar

```bash
python CODEtoGCal.py
```

Ce script :
- Lit le fichier `upcoming_magic_sets.csv`
- Crée des événements dans Google Calendar pour chaque date de sortie
- Utilise l'authentification OAuth pour accéder à votre calendrier
- Ajoute les événements dans le calendrier spécifié par l'ID

## Structure des fichiers

```
.
├── CODEDumper.py         # Script pour récupérer les sets via l'API Scryfall
├── CODEtoGCal.py         # Script pour créer des événements dans Google Calendar
├── WPDumper.py           # Script pour télécharger les fonds d'écran officiels
├── upcoming_magic_sets.csv # Données des prochains sets
├── requirements.txt      # Dépendances Python
├── .gitignore            # Fichiers ignorés par git
├── credentials.json      # Identifiants OAuth (non inclus, à créer)
├── token.pickle          # Token d'authentification (généré automatiquement)
└── resources/            # Dossier contenant les fonds d'écran téléchargés
```

## Notes

- Le script `WPDumper.py` tente de deviner les URLs des fonds d'écran sur le site de Wizards of the Coast, qui peuvent changer au fil du temps
- L'ID du calendrier dans `CODEtoGCal.py` doit être remplacé par l'ID de votre propre calendrier Google
- Les fichiers `credentials.json` et `token.pickle` contiennent des informations sensibles et sont donc exclus dans le `.gitignore`

## Licence

[Ajoutez ici les informations de licence selon votre préférence]
