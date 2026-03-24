import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Globale
BASE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = BASE_DIR / "resources"
DB_PATH = BASE_DIR / "database.sqlite"

# Google Calendar API
GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID")

# Scryfall API
SCRYFALL_API_URL = "https://api.scryfall.com/sets"

# Excluded set types
EXCLUDED_SET_TYPES = [
    'commander', 'promo', 'token', 'duel_deck', 'from_the_vault', 
    'spellbook', 'premium_deck', 'alchemy', 'archenemy', 'masterpiece', 
    'memorabilia', 'planechase', 'starter', 'treasure_chest', 'vanguard'
]

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(BASE_DIR / "app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("MGTAtoCal")
