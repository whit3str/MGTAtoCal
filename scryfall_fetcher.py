import requests
from datetime import datetime
from config import SCRYFALL_API_URL, EXCLUDED_SET_TYPES, logger
from database import add_or_update_sets

def fetch_upcoming_sets():
    """
    Fetch upcoming Magic: The Gathering sets from Scryfall API,
    filter out excluded types, limit to 10 latest, and store them in the database.
    """
    logger.info("Fetching upcoming sets from Scryfall...")
    try:
        response = requests.get(SCRYFALL_API_URL)
        response.raise_for_status()
        data = response.json()
        sets = data.get('data', [])

        filtered_sets = [s for s in sets if not any(keyword in s['set_type'] for keyword in EXCLUDED_SET_TYPES)]
        
        today = datetime.today().date()
        upcoming_sets = []
        
        for s in filtered_sets:
            if 'released_at' not in s:
                continue
            try:
                release_date = datetime.strptime(s['released_at'], '%Y-%m-%d').date()
                if release_date > today:
                    upcoming_sets.append({
                        'code': s['code'].upper(),
                        'name': s['name'],
                        'released_at': s['released_at']
                    })
            except ValueError:
                continue

        # Sort by release date and get the 10 closest ones
        latest_sets = sorted(upcoming_sets, key=lambda x: x['released_at'])[:10]
        
        if latest_sets:
            logger.info(f"Found {len(latest_sets)} valid upcoming sets.")
            add_or_update_sets(latest_sets)
            return latest_sets
        else:
            logger.info("No upcoming sets found.")
            return []

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching data from Scryfall: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in fetch_upcoming_sets: {e}")
        return []

if __name__ == "__main__":
    # Test execution
    from database import init_db
    init_db()
    fetch_upcoming_sets()
