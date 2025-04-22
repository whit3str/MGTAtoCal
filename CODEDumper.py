import requests
import pandas as pd
from datetime import datetime

# Définir l'URL de l'API Scryfall pour les sets
url = "https://api.scryfall.com/sets"

# Faire une requête GET à l'API
response = requests.get(url)

# Vérifier si la requête a réussi
if response.status_code == 200:
    # Analyser la réponse JSON
    data = response.json()

    # Obtenir la liste des sets
    sets = data['data']

    # Filtrer les sets pour exclure les types spécifiques
    excluded_types = ['commander', 'promo', 'token', 'duel_deck', 'from_the_vault', 'spellbook', 'premium_deck', 'alchemy', 'archenemy', 'masterpiece', 'memorabilia', 'planechase', 'starter', 'treasure_chest', 'vanguard']
    filtered_sets = [s for s in sets if not any(keyword in s['set_type'] for keyword in excluded_types)]

    # Obtenir la date du jour
    today = datetime.today().date()

    # Filtrer les sets pour inclure uniquement ceux qui ne sont pas encore sortis
    upcoming_sets = [s for s in filtered_sets if datetime.strptime(s['released_at'], '%Y-%m-%d').date() > today]

    # Trier les sets par date de sortie en ordre croissant et obtenir les 10 prochains sets
    latest_sets = sorted(upcoming_sets, key=lambda x: x['released_at'])[:10]

    # Créer un DataFrame à partir des sets sélectionnés
    df = pd.DataFrame(latest_sets)
    
    # Sélectionner uniquement les colonnes nécessaires
    df = df[['name', 'code', 'released_at']]

    # Convertir la colonne "code" en majuscules
    df['code'] = df['code'].str.upper()

    # Enregistrer le DataFrame dans un fichier CSV
    df.to_csv('upcoming_magic_sets.csv', index=False)

    print("Le fichier CSV a été généré avec succès.")
else:
    print(f"Échec de la récupération des données : {response.status_code}")