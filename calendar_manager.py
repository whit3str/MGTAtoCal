import pickle
from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from config import GOOGLE_CALENDAR_ID, BASE_DIR, logger
from database import get_pending_gcal, mark_gcal_done

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Authenticate and return the Google Calendar API service."""
    creds = None
    token_path = BASE_DIR / 'token.pickle'
    credentials_path = BASE_DIR / 'credentials.json'

    if token_path.exists():
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing Google Calendar Token...")
            try:
                creds.refresh(Request())
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                logger.error(f"Failed to refresh token: {e}")
                creds = None
                
        if not creds or not creds.valid:
            if not credentials_path.exists():
                logger.error(f"Missing {credentials_path.name}. Cannot authenticate with Google Calendar.")
                return None
            logger.info("Requesting new Google Calendar Token via browser...")
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

def sync_calendar_events():
    """Retrieve pending calendar events from DB and create them in Google Calendar."""
    if not GOOGLE_CALENDAR_ID:
        logger.error("GOOGLE_CALENDAR_ID is missing in .env configuration.")
        return

    pending_sets = get_pending_gcal()
    if not pending_sets:
        logger.info("No pending Google Calendar events to create.")
        return

    logger.info(f"Found {len(pending_sets)} sets requiring Google Calendar events.")
    
    service = get_calendar_service()
    if not service:
        logger.error("Failed to initialize Google Calendar service.")
        return

    successful = 0
    for s in pending_sets:
        try:
            # Validate date format
            release_date_str = s['release_date']
            release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()
            
            event = {
                'summary': f"MTG: {s['name']}",
                'description': f"Code: {s['code']}",
                'start': {
                    'date': release_date.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'date': release_date.isoformat(),
                    'timeZone': 'UTC',
                },
            }

            created_event = service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event).execute()
            logger.info(f"Event created for {s['code']}: {created_event.get('htmlLink')}")
            
            mark_gcal_done(s['code'])
            successful += 1
            
        except Exception as e:
            logger.error(f"Failed to create Google Calendar event for {s['code']}: {e}")

    logger.info(f"Calendar sync completed. Successfully created {successful}/{len(pending_sets)} events.")

if __name__ == "__main__":
    sync_calendar_events()
