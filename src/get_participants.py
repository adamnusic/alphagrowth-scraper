import csv
import requests
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random

def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # number of retries
        backoff_factor=1,  # wait 1, 2, 4 seconds between retries
        status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def get_participants_from_csv(csv_filename):
    all_participants = {}
    session = create_session()
    
    with open(csv_filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        space_urls = [row['url'] for row in reader]

    for idx, space_url in enumerate(space_urls, 1):
        print(f"Fetching participants from {space_url} ({idx}/{len(space_urls)})...")
        try:
            # Add random delay between 1-3 seconds to avoid rate limiting
            time.sleep(1 + random.random() * 2)
            
            response = session.get(space_url, timeout=30)  # Add timeout
            if response.status_code != 200:
                print(f"Failed to fetch {space_url} - Status code: {response.status_code}")
                all_participants[space_url] = {'hosts': [], 'speakers': []}
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            participants = {'hosts': [], 'speakers': []}

            def extract_participant_info(header_text):
                try:
                    h2 = soup.find('h2', class_='hero-title', string=header_text)
                    if not h2:
                        print(f"No {header_text} section found for {space_url}")
                        return []

                    container = h2.find_next_sibling()
                    if not container:
                        print(f"No container found for {header_text} in {space_url}")
                        return []

                    results = []
                    name_links = container.select('a.text-white[href^="/spaces/participant/"]')
                    twitter_links = container.select('a[href^="https://twitter.com/"]')

                    for i, name_link in enumerate(name_links):
                        participant = {
                            'name': name_link.text.strip(),
                            'alphagrowth_link': "https://alphagrowth.io" + name_link['href'],
                            'twitter_link': twitter_links[i]['href'] if i < len(twitter_links) else None
                        }
                        results.append(participant)

                    return results
                except Exception as e:
                    print(f"Error extracting {header_text} info from {space_url}: {str(e)}")
                    return []

            # Try to get hosts and speakers, continue even if one fails
            participants['hosts'] = extract_participant_info('Host')
            participants['speakers'] = extract_participant_info('Speaker')

            all_participants[space_url] = participants

        except requests.exceptions.RequestException as e:
            print(f"Network error processing {space_url}: {str(e)}")
            all_participants[space_url] = {'hosts': [], 'speakers': []}
        except Exception as e:
            print(f"Unexpected error processing {space_url}: {str(e)}")
            all_participants[space_url] = {'hosts': [], 'speakers': []}

    return all_participants

def save_participants_to_csv(participants, output_path):
    # Create the data directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(['space_url', 'role', 'name', 'alphagrowth_link', 'twitter_link'])
        
        # Write data
        for space_url, data in participants.items():
            for role in ['hosts', 'speakers']:
                for participant in data[role]:
                    writer.writerow([
                        space_url,
                        role,
                        participant['name'],
                        participant['alphagrowth_link'],
                        participant['twitter_link']
                    ])

if __name__ == "__main__":
    # Get the script directory and construct paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    
    # Find the most recent space_urls CSV file
    space_urls_files = [f for f in os.listdir(data_dir) if f.startswith('space_urls_') and f.endswith('.csv')]
    if not space_urls_files:
        print("No space_urls CSV file found in data directory!")
        sys.exit(1)
    
    latest_space_urls = sorted(space_urls_files)[-1]
    space_urls_path = os.path.join(data_dir, latest_space_urls)
    
    # Generate output filename with current date
    output_filename = f'participants_{datetime.now().strftime("%Y%m%d")}.csv'
    output_path = os.path.join(data_dir, output_filename)
    
    print(f"Reading space URLs from: {space_urls_path}")
    print(f"Will save participants to: {output_path}")
    
    # Get and save participants
    participants = get_participants_from_csv(space_urls_path)
    save_participants_to_csv(participants, output_path)
    
    # Print summary
    total_hosts = sum(len(p['hosts']) for p in participants.values())
    total_speakers = sum(len(p['speakers']) for p in participants.values())
    print(f"\nSummary:")
    print(f"Total spaces processed: {len(participants)}")
    print(f"Total hosts found: {total_hosts}")
    print(f"Total speakers found: {total_speakers}")
    print(f"Results saved to: {output_path}")
