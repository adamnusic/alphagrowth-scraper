import argparse
import sys
import os
from get_space_urls import get_space_links_and_save_csv
from get_participants import get_participants_from_csv

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
        except Exception as e:
            print(f"Error during participant retrieval: {e}")
            sys.exit(1)
    else:
        print('Unknown command')
        sys.exit(1)

if __name__ == '__main__':
    main()
