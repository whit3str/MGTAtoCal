# MGTAtoCal - MTG Release Tracker & Automator

A modern toolkit to track upcoming Magic: The Gathering releases, automatically download official wallpapers, and sync release dates to your Google Calendar. Now featuring a web dashboard and Docker support.

## Features

- **Automated Tracking**: Fetches upcoming sets from the Scryfall API.
- **Wallpaper Downloader**: Automatically finds and downloads high-resolution (1920x1080) marketing wallpapers.
- **Calendar Sync**: Creates events in your Google Calendar for every MTG set release.
- **Web Dashboard**: A beautiful FastAPI-based interface to monitor and trigger tasks.
- **Dockerized**: Easy deployment with Docker and Docker Compose.
- **Daily Automation**: Built-in scheduler runs a full sync every 24 hours.

## Quick Start (Docker)

The easiest way to run MGTAtoCal is using Docker.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/MGTAtoCal.git
    cd MGTAtoCal
    ```

2.  **Configure Environment**:
    - Copy `.env.example` to `.env`.
    - Set your `GOOGLE_CALENDAR_ID` in the `.env` file.

3.  **Google API Setup**:
    - Place your `credentials.json` (OAuth Client ID) in the root directory.
    - Run the initial authentication once on your host machine to generate `token.pickle` (see [OAuth Setup](#oauth-setup)).

4.  **Run with Docker Compose**:
    ```bash
    docker-compose up -d
    ```
    Access the dashboard at `http://localhost:8000`.

## Manual Installation

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Usage**:
    - Run the web dashboard: `python web.py`
    - Or use the CLI orchestrator:
      - `python main.py --fetch` (Update database from Scryfall)
      - `python main.py --wallpapers` (Download missing wallpapers)
      - `python main.py --calendar` (Sync to Google Calendar)
      - `python main.py --all` (Run everything)

## Project Structure

- `web.py`: FastAPI web server and dashboard.
- `main.py`: CLI orchestrator.
- `scryfall_fetcher.py`: Scryfall API integration.
- `wallpaper_downloader.py`: Intelligent wallpaper scraping and extraction.
- `calendar_manager.py`: Google Calendar API integration.
- `database.py`: SQLite state management.
- `config.py`: Centralized configuration and logging.
- `resources/`: Downloaded wallpapers storage.

## OAuth Setup

To use Google Calendar, you need to:
1.  Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2.  Enable the **Google Calendar API**.
3.  Create **OAuth Client ID** credentials (Desktop App).
4.  Download the JSON and rename it to `credentials.json` in the root folder.
5.  Run `python calendar_manager.py` once locally to open the browser for initial authorization. This creates `token.pickle`.

## License

MIT License - Feel free to use and contribute!
