import requests
from bs4 import BeautifulSoup
import time
import csv
import os
from datetime import datetime

BASE_URL = "https://alphagrowth.io/spaces/?page="

def get_space_links():
    space_urls = []
    for page in range(1, 325):
        print(f"Fetching page {page}...")
        response = requests.get(f"{BASE_URL}{page}")
        if response.status_code != 200:
            print(f"Failed to fetch page {page}")
            continue
        soup = BeautifulSoup(response.text, 'html.parser')

        # Select all <li> elements with 'onclick' attribute containing /spaces/
        elements = soup.select('li[onclick*="/spaces/"]')

        for elem in elements:
            onclick_value = elem.get('onclick', '')
            # Extract the URL path inside the onclick string
            # Example onclick: window.location='/spaces/web3-and-chill-ccd';
            if "window.location=" in onclick_value:
                start = onclick_value.find("'") + 1
                end = onclick_value.rfind("'")
                path = onclick_value[start:end]
                full_url = "https://alphagrowth.io" + path
                space_urls.append(full_url)

        time.sleep(1)  # polite delay between requests
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