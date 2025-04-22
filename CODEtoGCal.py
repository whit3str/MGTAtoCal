import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# Charger les événements depuis le fichier CSV
df = pd.read_csv('upcoming_magic_sets.csv')

# Convertir les dates de sortie en objets datetime
df['released_at'] = pd.to_datetime(df['released_at'])

# Créer une liste d'événements pour Google Calendar
events = []
for index, row in df.iterrows():
    event = {
        'summary': f"MTG: {row['name']}",
        'description': f"Code: {row['code']}",
        'start': {
            'date': row['released_at'].date().isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'date': row['released_at'].date().isoformat(),
            'timeZone': 'UTC',
        },
    }
    events.append(event)

# Authentification et création du service Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None

# Le fichier token.pickle stocke les jetons d'accès et d'actualisation de l'utilisateur
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

# Si il n'y a pas de jeton valide, laissez l'utilisateur se connecter
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)

# Spécifier l'ID de l'agenda
calendar_id = '0a0601ade1046f12fd24a7b0810c5063e3158bbbbdf195fd825da672f8abdeaf@group.calendar.google.com'

# Ajouter les événements au calendrier spécifié
for event in events:
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")

print("Tous les événements ont été créés avec succès dans l'agenda spécifié.")
