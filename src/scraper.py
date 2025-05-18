import argparse
import sys
import os
from get_space_urls import get_space_links_and_save_csv
from get_participants import get_participants_from_csv
import csv
from datetime import datetime

# Define constants for file paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV_PATH = os.path.join(SCRIPT_DIR, '..', 'data', 'space_urls.csv')

def main():
    parser = argparse.ArgumentParser(description='AlphaGrowth Spaces Scraper')
    parser.add_argument('command', choices=['get_urls', 'get_participants'],
                        help='Command to run: get_urls or get_participants')
    parser.add_argument('--urls_csv', default=DEFAULT_CSV_PATH,
                        help='CSV file to save/read space URLs')

    args = parser.parse_args()

    if args.command == 'get_urls':
        print('Running URL retrieval...')
        try:
            get_space_links_and_save_csv(args.urls_csv)
        except Exception as e:
            print(f"Error during URL retrieval: {e}")
            sys.exit(1)
    elif args.command == 'get_participants':
        print('Running participant retrieval...')
        try:
            participants = get_participants_from_csv(args.urls_csv)
            total_hosts = sum(len(p['hosts']) for p in participants.values())
            total_speakers = sum(len(p['speakers']) for p in participants.values())
            print(f'Total hosts found: {total_hosts}')
            print(f'Total speakers found: {total_speakers}')
            
            # Save participants to CSV
            output_filename = f'participants_{datetime.now().strftime("%Y%m%d")}.csv'
            output_path = os.path.join(os.path.dirname(args.urls_csv), output_filename)
            
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
            
            print(f'Results saved to: {output_path}')
        except Exception as e:
            print(f"Error during participant retrieval: {e}")
            sys.exit(1)
    else:
        print('Unknown command')
        sys.exit(1)

if __name__ == '__main__':
    main()
