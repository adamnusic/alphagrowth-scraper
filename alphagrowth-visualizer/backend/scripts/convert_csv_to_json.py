import pandas as pd
import json
import os
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_csv_to_json():
    try:
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)

        # Convert participants data
        logger.info("Reading participants CSV...")
        participants_df = pd.read_csv(os.path.join(data_dir, 'participants.csv'))
        
        # Group by name to count spaces and determine roles
        participant_stats = defaultdict(lambda: {'spaces': 0, 'roles': set(), 'twitter': ''})
        
        for _, row in participants_df.iterrows():
            name = row['name']
            participant_stats[name]['spaces'] += 1
            participant_stats[name]['roles'].add(row['role'])
            if pd.notna(row['twitter_link']):
                participant_stats[name]['twitter'] = row['twitter_link']
        
        # Transform to final format
        participants_data = []
        name_to_id = {}
        for idx, (name, stats) in enumerate(participant_stats.items(), start=1):
            # Determine role
            roles = stats['roles']
            if len(roles) > 1:
                role = 'both'
            else:
                role = list(roles)[0]
            
            participant = {
                'id': str(idx),  # Generate sequential IDs
                'name': name,
                'role': role,
                'spaces': stats['spaces'],
                'twitter': stats['twitter']
            }
            participants_data.append(participant)
            name_to_id[name] = str(idx)
        
        logger.info(f"Processed {len(participants_data)} participants")
        
        # Save participants data
        with open(os.path.join(data_dir, 'participants_data.json'), 'w') as f:
            json.dump(participants_data, f, indent=2)
        logger.info("Saved participants data to JSON")

        # Build network data from participants.csv only
        logger.info("Building network data from participants.csv...")
        network_data = {
            'nodes': participants_data,
            'links': []
        }
        
        # Create links between participants in the same space
        space_participants = defaultdict(set)
        for _, row in participants_df.iterrows():
            space_participants[row['space_url']].add(row['name'])
        
        for space, participants in space_participants.items():
            participants = list(participants)
            for i in range(len(participants)):
                for j in range(i + 1, len(participants)):
                    link = {
                        'source': name_to_id[participants[i]],
                        'target': name_to_id[participants[j]],
                        'value': 1
                    }
                    network_data['links'].append(link)
        
        logger.info(f"Processed {len(network_data['nodes'])} nodes and {len(network_data['links'])} links")
        
        # Save network data
        with open(os.path.join(data_dir, 'network_data.json'), 'w') as f:
            json.dump(network_data, f, indent=2)
        logger.info("Saved network data to JSON")
        
        return True
    except Exception as e:
        logger.error(f"Error converting CSV to JSON: {str(e)}")
        return False

if __name__ == '__main__':
    success = convert_csv_to_json()
    if not success:
        exit(1) 