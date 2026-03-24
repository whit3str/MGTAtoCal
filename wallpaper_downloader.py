import requests
import zipfile
import shutil
from datetime import datetime
from pathlib import Path
from config import RESOURCES_DIR, logger
from database import get_pending_wallpapers, mark_wallpaper_done

def download_and_extract_zip(url: str, temp_extract_path: Path) -> bool:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        if temp_extract_path.exists():
            shutil.rmtree(temp_extract_path)
        temp_extract_path.mkdir(parents=True, exist_ok=True)
        
        zip_path = temp_extract_path / 'temp.zip'
        
        with open(zip_path, 'wb') as file:
            file.write(response.content)
            
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_path)
            zip_path.unlink()
            return True
        except zipfile.BadZipFile:
            logger.error(f"Error: {zip_path} is not a valid ZIP file.")
            zip_path.unlink()
            return False
            
    except requests.exceptions.RequestException as e:
        logger.debug(f"Failed downloading from {url}: {e}")
        return False

def find_wallpapers(directory: Path) -> list[Path]:
    """Find the best available wallpaper in the directory."""
    # Priority 1: Exact 1920x1080 resolution in name
    wallpapers = [p for p in directory.rglob('*') if p.is_file() and '1920x1080' in p.name]
    if wallpapers:
        return wallpapers

    # Priority 2: Other high resolutions (e.g. 2560x1440, 4k)
    resolutions = ['2560x1440', '3840x2160', 'ultra_wide']
    for res in resolutions:
        wallpapers = [p for p in directory.rglob('*') if p.is_file() and res in p.name]
        if wallpapers:
            logger.info(f"Found alternative resolution wallpaper: {res}")
            return wallpapers

    # Priority 3: Keywords 'wallpaper' or 'keyart' or 'digital_asset'
    keywords = ['wallpaper', 'keyart', 'marketing', 'land']
    for kw in keywords:
        wallpapers = [p for p in directory.rglob('*') if p.is_file() and kw in p.name.lower() and p.suffix.lower() in ['.jpg', '.jpeg', '.png']]
        if wallpapers:
            logger.info(f"Found wallpaper using keyword: {kw}")
            return wallpapers

    # Final Fallback: Any large image file
    all_images = [p for p in directory.rglob('*') if p.is_file() and p.suffix.lower() in ['.jpg', '.jpeg', '.png']]
    if all_images:
        # Sort by size to get the largest image
        all_images.sort(key=lambda x: x.stat().st_size, reverse=True)
        logger.info(f"Falling back to largest image: {all_images[0].name} ({all_images[0].stat().st_size / 1024:.1f} KB)")
        return [all_images[0]]

    return []

def try_download_and_process(base_url: str, code: str, temp_extract_path: Path) -> bool:
    """Try to download each ZIP variant and find a wallpaper within it."""
    variants = [
        f"{code.lower()}_sma_key_en.zip",
        f"{code.lower()}_sma_key.zip",
        f"{code.lower()}_sma_en.zip",
        f"{code.lower()}_sma.zip",
        f"{code.lower()}_alg_en.zip",
        f"{code.lower()}_alg.zip"
    ]
    
    for variant in variants:
        url = f"{base_url}/{code.lower()}/{variant}"
        # We try to download and extract this specific variant
        if download_and_extract_zip(url, temp_extract_path):
            # Then we look for wallpapers inside
            if process_wallpapers(code, temp_extract_path):
                return True
            else:
                logger.info(f"Variant {variant} found but contained no valid wallpaper. Trying next...")
    
    return False

def process_extension(name: str, code: str, release_date: str) -> bool:
    RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
    temp_extract_path = RESOURCES_DIR / f"temp_{code.lower()}"
    
    try:
        release_year = datetime.strptime(release_date, "%Y-%m-%d").year
    except ValueError:
        logger.warning(f"Invalid release date format: {release_date}, using current year")
        release_year = datetime.now().year
    
    logger.info(f"Processing extension: {name} ({code}), release year: {release_year}")
    
    success = False
    # Try current year, then previous, then next
    for year_offset in [0, -1, 1]:
        base_url = f'https://media.wizards.com/{release_year + year_offset}/wpn/marketing_materials'
        if try_download_and_process(base_url, code, temp_extract_path):
            success = True
            break
                
    if not success:
        logger.warning(f"Failed to find wallpaper for {code} after trying all year/variant combinations.")
    
    # Clean up temp folder
    if temp_extract_path.exists():
        shutil.rmtree(temp_extract_path)
        
    return success

def process_wallpapers(code: str, temp_extract_path: Path) -> bool:
    """Process all wallpapers after successful download and extraction"""
    wallpapers = find_wallpapers(temp_extract_path)
    
    if wallpapers:
        logger.info(f'Found {len(wallpapers)} wallpaper candidate(s) for {code}.')
        
        wallpaper_path = wallpapers[0]
        # Check resolution if possible, or just use the suffix
        suffix = wallpaper_path.suffix
        res_tag = "1920x1080" if "1920x1080" in wallpaper_path.name else "hi-res"
        destination = RESOURCES_DIR / f"{code}_wallpaper_{res_tag}{suffix}"
        
        shutil.copy2(wallpaper_path, destination)
        logger.info(f'Saved wallpaper as: {destination.name}')
        return True
    else:
        # Log all files to help debugging if nothing found
        files_found = [p.name for p in temp_extract_path.rglob('*') if p.is_file()]
        logger.warning(f"No wallpapers found inside ZIP for {code}. Files present: {files_found}")
        return False

def download_missing_wallpapers():
    """Retrieve all pending sets from DB and download their wallpapers."""
    pending_sets = get_pending_wallpapers()
    
    if not pending_sets:
        logger.info("No pending wallpapers to download.")
        return
        
    logger.info(f"Found {len(pending_sets)} sets requiring wallpaper download.")
    
    successful = 0
    for s in pending_sets:
        code = s['code']
        if process_extension(s['name'], code, s['release_date']):
            successful += 1
            mark_wallpaper_done(code)
            
    logger.info(f"Wallpaper processing completed. Successfully downloaded {successful}/{len(pending_sets)}.")

if __name__ == "__main__":
    download_missing_wallpapers()
