import requests
import zipfile
import os
import csv
import shutil
from datetime import datetime

def download_and_extract_zip(url, extract_to='.', temp_subfolder='temp_extract'):
    print(f"Attempting to download ZIP file from {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Create resources directory if it doesn't exist
        os.makedirs(os.path.join(extract_to, 'resources'), exist_ok=True)
        
        # Create a temporary subfolder for this specific extraction
        temp_extract_path = os.path.join(extract_to, 'resources', temp_subfolder)
        if os.path.exists(temp_extract_path):
            shutil.rmtree(temp_extract_path)
        os.makedirs(temp_extract_path)
        
        zip_path = os.path.join(temp_extract_path, 'temp.zip')
        
        with open(zip_path, 'wb') as file:
            file.write(response.content)
        
        print(f"Extracting ZIP file to {temp_extract_path}")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_path)
            print(f"Deleted temporary ZIP file {zip_path}")
            os.remove(zip_path)
            return True
        except zipfile.BadZipFile:
            print(f"Error: {zip_path} is not a valid ZIP file.")
            os.remove(zip_path)
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return False

def find_wallpapers(directory):
    """Find all files containing '1920x1080' in the directory"""
    print(f"Searching for wallpapers containing '1920x1080' in directory {directory}")
    wallpapers = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if '1920x1080' in file:
                wallpapers.append(os.path.join(root, file))
    return wallpapers

def try_download_variants(base_url, short_name, extract_to='.', temp_subfolder='temp_extract'):
    """Try different variants of the ZIP file name"""
    # List of possible file name patterns
    variants = [
        f"{short_name.lower()}_alg.zip",
        f"{short_name.lower()}_alg_en.zip"
    ]
    
    for variant in variants:
        url = f"{base_url}/{short_name.lower()}/{variant}"
        print(f"Trying variant: {url}")
        if download_and_extract_zip(url, extract_to, temp_subfolder):
            print(f"Successfully downloaded and extracted: {variant}")
            return True
    
    return False

def process_extension(name, short_name, release_date):
    # Create a unique temporary subfolder for this extension
    temp_subfolder = f"temp_{short_name.lower()}"
    
    # Extract the year from the release date
    try:
        release_year = datetime.strptime(release_date, "%Y-%m-%d").year
    except ValueError:
        print(f"Invalid release date format: {release_date}, using current year")
        release_year = datetime.now().year
    
    print(f"Processing extension: {name} with code: {short_name}, release year: {release_year}")
    
    # Try with the original release year
    base_url = f'https://media.wizards.com/{release_year}/wpn/marketing_materials'
    if try_download_variants(base_url, short_name, temp_subfolder=temp_subfolder):
        return process_wallpapers(short_name, temp_subfolder)
    
    # If failed, try with the previous year
    print(f"Trying with previous year: {release_year - 1}")
    base_url = f'https://media.wizards.com/{release_year - 1}/wpn/marketing_materials'
    if try_download_variants(base_url, short_name, temp_subfolder=temp_subfolder):
        return process_wallpapers(short_name, temp_subfolder)
    
    # If still failed, try with the next year
    print(f"Trying with next year: {release_year + 1}")
    base_url = f'https://media.wizards.com/{release_year + 1}/wpn/marketing_materials'
    if try_download_variants(base_url, short_name, temp_subfolder=temp_subfolder):
        return process_wallpapers(short_name, temp_subfolder)
    
    # Clean up the temporary subfolder if all attempts failed
    temp_extract_path = os.path.join('.', 'resources', temp_subfolder)
    if os.path.exists(temp_extract_path):
        shutil.rmtree(temp_extract_path)
    
    print(f"Failed to download or extract ZIP for {short_name} after trying all year variants")
    return False

def process_wallpapers(short_name, temp_subfolder):
    """Process all wallpapers after successful download and extraction"""
    temp_extract_path = os.path.join('.', 'resources', temp_subfolder)
    wallpapers = find_wallpapers(temp_extract_path)
    
    if wallpapers:
        print(f'Found {len(wallpapers)} wallpaper(s) for {short_name}')
        
        # Process only the first wallpaper to ensure consistent naming
        wallpaper_path = wallpapers[0]
        file_ext = os.path.splitext(wallpaper_path)[1]
        
        # Create a standardized destination filename
        destination = os.path.join('resources', f"{short_name}_wallpaper_1920x1080{file_ext}")
        
        # Copy and rename the wallpaper to the resources folder
        shutil.copy2(wallpaper_path, destination)
        print(f'Saved wallpaper as: {destination}')
        
        # Clean up the temporary subfolder
        if os.path.exists(temp_extract_path):
            shutil.rmtree(temp_extract_path)
            print(f'Removed temporary extraction folder: {temp_extract_path}')
        
        return True
    else:
        print(f'No wallpapers found for {short_name}.')
        # Clean up the temporary subfolder
        if os.path.exists(temp_extract_path):
            shutil.rmtree(temp_extract_path)
            print(f'Removed temporary extraction folder: {temp_extract_path}')
        return False

# Create resources folder if it doesn't exist
if not os.path.exists('resources'):
    os.makedirs('resources')
else:
    # Clean up any existing wallpapers to avoid confusion
    for file in os.listdir('resources'):
        file_path = os.path.join('resources', file)
        if os.path.isfile(file_path) and ('wallpaper' in file or '1920x1080' in file):
            os.remove(file_path)
            print(f"Removed existing wallpaper: {file_path}")

# Read data from the CSV file in the same directory
csv_file = 'upcoming_magic_sets.csv'  # Using the filename from your document
print(f"Reading data from CSV file: {csv_file}")

try:
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        extensions = list(reader)
    
    # Process each extension from the CSV
    successful_downloads = 0
    failed_downloads = []
    
    for extension in extensions:
        name = extension['name']
        code = extension['code']
        release_date = extension['released_at']
        
        print(f"\nProcessing: {name} ({code}) - Release date: {release_date}")
        if process_extension(name, code, release_date):
            successful_downloads += 1
        else:
            failed_downloads.append(f"{name} ({code})")
    
    print(f"\nScript execution completed. Successfully downloaded {successful_downloads} out of {len(extensions)} wallpapers.")
    
    if failed_downloads:
        print("\nFailed downloads:")
        for failed in failed_downloads:
            print(f"- {failed}")

except FileNotFoundError:
    print(f"Error: CSV file '{csv_file}' not found.")
except Exception as e:
    print(f"Error processing CSV file: {e}")