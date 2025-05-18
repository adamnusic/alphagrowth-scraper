import requests
from bs4 import BeautifulSoup
import time
import csv
import os
from datetime import datetime
import json

BASE_URL = "https://alphagrowth.io/spaces/?page="

def load_existing_spaces():
    """Load existing spaces from the CSV file."""
    try:
        # Look for the most recent space_urls CSV file
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        space_urls_files = [f for f in os.listdir(data_dir) if f.startswith('space_urls_') and f.endswith('.csv')]
        
        if not space_urls_files:
            print("No space_urls CSV file found!")
            return set()
            
        latest_file = sorted(space_urls_files)[-1]
        csv_path = os.path.join(data_dir, latest_file)
        
        existing_spaces = set()
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_spaces.add(row['url'])
                
        print(f"Loaded existing spaces from {latest_file}: {sorted(list(existing_spaces))[:5]}...")  # Print first 5 for debugging
        return existing_spaces
    except Exception as e:
        print(f"Error loading existing spaces: {str(e)}")
        return set()

def get_space_links():
    space_urls = []
    existing_spaces = load_existing_spaces()
    print(f"Found {len(existing_spaces)} existing spaces")
    
    page = 1
    while True:
        print(f"\nFetching page {page}...")
        try:
            response = requests.get(f"{BASE_URL}{page}")
            print(f"Response status code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Failed to fetch page {page}")
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            elements = soup.select('li[onclick*="/spaces/"]')
            print(f"Found {len(elements)} space elements on page {page}")
            
            if not elements:
                print("No more spaces found")
                break
                
            found_existing = False
            for elem in elements:
                onclick_value = elem.get('onclick', '')
                if "window.location=" in onclick_value:
                    start = onclick_value.find("'") + 1
                    end = onclick_value.rfind("'")
                    path = onclick_value[start:end]
                    full_url = "https://alphagrowth.io" + path
                    
                    # If we find an existing space, we can stop
                    if full_url in existing_spaces:
                        print(f"Found existing space: {full_url}")
                        found_existing = True
                        break
                        
                    space_urls.append(full_url)
                    print(f"Added new space: {full_url}")
            
            if found_existing:
                print("Found existing space, stopping")
                break
                
            page += 1
            time.sleep(1)  # polite delay between requests
            
        except Exception as e:
            print(f"Error processing page {page}: {str(e)}")
            break
    
    print(f"\nFound {len(space_urls)} new spaces")
    return space_urls

def get_space_links_and_save_csv(output_path):
    # Create the data directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Get the space URLs
    links = get_space_links()
    
    # Save to CSV
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['url'])  # header
        for url in links:
            writer.writerow([url])
    
    print(f"Saved {len(links)} URLs to {output_path}")
    print("Sample of first 10 URLs:")
    for url in links[:10]:
        print(url)

if __name__ == "__main__":
    # When run directly, save to data/space_urls.csv
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_output = os.path.join(script_dir, '..', 'data', f'space_urls_{datetime.now().strftime("%Y%m%d")}.csv')
    get_space_links_and_save_csv(default_output)