import argparse
from config import logger
from database import init_db
from scryfall_fetcher import fetch_upcoming_sets
from wallpaper_downloader import download_missing_wallpapers
from calendar_manager import sync_calendar_events

def main():
    parser = argparse.ArgumentParser(description="MTG Release Tracker - Fetch Sets, Download Wallpapers, Sync Calendar")
    parser.add_argument('--fetch', action='store_true', help="Fetch upcoming sets from Scryfall API")
    parser.add_argument('--wallpapers', action='store_true', help="Download wallpapers for missing sets")
    parser.add_argument('--calendar', action='store_true', help="Create Google Calendar events for missing sets")
    parser.add_argument('--all', action='store_true', help="Run all tasks sequentially")
    
    args = parser.parse_args()

    # Initialize the database automatically
    init_db()

    if not any([args.fetch, args.wallpapers, args.calendar, args.all]):
        parser.print_help()
        return

    if args.fetch or args.all:
        logger.info("=== Starting Scryfall Fetch ===")
        fetch_upcoming_sets()

    if args.wallpapers or args.all:
        logger.info("=== Starting Wallpaper Download ===")
        download_missing_wallpapers()

    if args.calendar or args.all:
        logger.info("=== Starting Google Calendar Sync ===")
        sync_calendar_events()
        
    logger.info("=== All Tasks Completed ===")

if __name__ == "__main__":
    main()
