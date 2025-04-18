import requests
import zipfile
import os
import csv
import shutil

def download_and_extract_zip(url, extract_to='.'):
    print(f"Downloading ZIP file from {url}")
    response = requests.get(url)
    zip_path = os.path.join(extract_to, 'resources', 'temp.zip')
    
    with open(zip_path, 'wb') as file:
        file.write(response.content)
    
    print(f"Extracting ZIP file to {os.path.join(extract_to, 'resources')}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.join(extract_to, 'resources'))
        print(f"Deleted temporary ZIP file {zip_path}")
        os.remove(zip_path)
    except zipfile.BadZipFile:
        print(f"Error: {zip_path} is not a valid ZIP file.")
        os.remove(zip_path)

def find_wallpaper(directory):
    print(f"Searching for wallpaper containing '1920x1080' in directory {directory}")
    for root, dirs, files in os.walk(directory):
        for file in files:
            if '1920x1080' in file:
                return os.path.join(root, file)
    return None

def process_extensions(base_url, short_name):
    url = f"{base_url}/{short_name}/{short_name}_alg.zip"
    download_and_extract_zip(url, extract_to='.')
    wallpaper_path = find_wallpaper(os.path.join('.', 'resources'))
    
    if wallpaper_path:
        print(f'Wallpaper found for {short_name}: {wallpaper_path}')
        # Move the wallpaper to the resources folder
        shutil.move(wallpaper_path, os.path.join('resources', os.path.basename(wallpaper_path)))
        print(f'Moved wallpaper to resources folder: {os.path.join("resources", os.path.basename(wallpaper_path))}')
        
        # Remove all other extracted folders and files
        for root, dirs, files in os.walk(os.path.join('.', 'resources')):
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))
            for file in files:
                if '1920x1080' not in file:
                    os.remove(os.path.join(root, file))
        print('Removed all other extracted folders and files.')
    else:
        print(f'Wallpaper not found for {short_name}.')

# Read data from CSV file
with open('upcoming_magic_sets.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    extensions = list(reader)

# Base URL for marketing materials
base_url = 'https://media.wizards.com/2025/wpn/marketing_materials'

# Create resources folder if it doesn't exist
if not os.path.exists('resources'):
    os.makedirs('resources')

# Process extensions using data from CSV file
for extension in extensions:
    short_name = extension['code'].lower()
    print(f"Processing extension: {extension['name']} with short name: {short_name}")
    process_extensions(base_url, short_name)

print("Script execution completed.")
