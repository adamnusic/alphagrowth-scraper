import pandas as pd
import json
from collections import defaultdict
from typing import Dict, List, Any
import os
from datetime import datetime
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sanitize_name(name: str) -> str:
    """Convert a name to a valid ID by removing special characters and spaces"""
    # Remove emojis and special characters
    name = re.sub(r'[^\w\s-]', '', name)
    # Replace spaces with underscores
    name = re.sub(r'\s+', '_', name)
    # Remove any remaining special characters
    name = re.sub(r'[^a-zA-Z0-9_-]', '', name)
    return name

class ParticipantNode:
    def __init__(self, name: str):
        self.original_name = name
        self.name = sanitize_name(name)
        self.twitter = None
        self.alphagrowth_link = None
        self.host_spaces: List[str] = []
        self.speaker_spaces: List[str] = []
        self.total_spaces = 0
        self.node_color = None

    def add_space(self, space_url: str, role: str):
        if role == 'host':
            self.host_spaces.append(space_url)
        else:
            self.speaker_spaces.append(space_url)
        self.total_spaces = len(self.host_spaces) + len(self.speaker_spaces)
        self._update_color()

    def _update_color(self):
        """Update node color based on roles"""
        if self.host_spaces and self.speaker_spaces:
            self.node_color = '#FFA500'  # Orange for both
        elif self.host_spaces:
            self.node_color = '#FF0000'  # Red for host
        else:
            self.node_color = '#0000FF'  # Blue for speaker

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.original_name,
            'id': self.name,
            'twitter': self.twitter,
            'alphagrowth_link': self.alphagrowth_link,
            'host_spaces': self.host_spaces,
            'speaker_spaces': self.speaker_spaces,
            'total_spaces': self.total_spaces,
            'node_color': self.node_color
        }

def find_latest_participants_file() -> str:
    """Find the most recent participants CSV file in the data directory"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    files = [f for f in os.listdir(data_dir) if f.startswith('participants_') and f.endswith('.csv')]
    if not files:
        raise FileNotFoundError("No participants CSV file found")
    return os.path.join(data_dir, sorted(files)[-1])

def process_participants_data(csv_path: str = None) -> Dict[str, ParticipantNode]:
    """Process the participants CSV and create a network of participants"""
    if csv_path is None:
        csv_path = find_latest_participants_file()
    
    logger.info(f"Processing data from: {csv_path}")
    
    # Read the CSV
    df = pd.read_csv(csv_path)
    
    # Debug: Print column names and first few rows
    logger.info(f"\nCSV Columns: {df.columns.tolist()}")
    logger.info(f"\nFirst few rows:\n{df.head()}")
    
    # Debug: Print unique role values
    logger.info(f"\nUnique role values: {df['role'].unique()}")
    
    # Create participant nodes
    participants: Dict[str, ParticipantNode] = {}
    
    # Process each row
    for _, row in df.iterrows():
        # Skip rows with NaN values in required fields
        if pd.isna(row['name']) or pd.isna(row['role']) or pd.isna(row['space_url']):
            continue
            
        name = str(row['name'])
        # Normalize role to singular (e.g., 'hosts' -> 'host', 'speakers' -> 'speaker')
        role = str(row['role']).rstrip('s').lower()
        
        if name not in participants:
            participants[name] = ParticipantNode(name)
            participants[name].twitter = str(row['twitter_link']) if not pd.isna(row['twitter_link']) else None
            participants[name].alphagrowth_link = str(row['alphagrowth_link']) if not pd.isna(row['alphagrowth_link']) else None
        
        participants[name].add_space(str(row['space_url']), role)
    
    logger.info(f"\nProcessed {len(participants)} unique participants")
    return participants

def generate_network_data(participants: Dict[str, ParticipantNode]) -> Dict[str, Any]:
    """Generate network graph data structure"""
    # Sort participants by total spaces and take top 1000
    top_participants = sorted(participants.values(), key=lambda x: x.total_spaces, reverse=True)[:1000]
    
    nodes = []
    links = []
    
    # Create nodes for top participants
    for participant in top_participants:
        nodes.append({
            'id': participant.name,
            'size': participant.total_spaces,
            'color': participant.node_color,
            'name': participant.original_name,
            'twitter': participant.twitter
        })
    
    # Create links between participants who have been in the same spaces
    space_participants = defaultdict(set)
    for participant in top_participants:
        for space in participant.host_spaces + participant.speaker_spaces:
            space_participants[space].add(participant.name)
    
    # Generate links between participants in the same spaces
    # Limit to 5 links per participant to keep the network manageable
    participant_links = defaultdict(int)
    for space, participants_in_space in space_participants.items():
        participants_list = list(participants_in_space)
        for i in range(len(participants_list)):
            for j in range(i + 1, len(participants_list)):
                p1, p2 = participants_list[i], participants_list[j]
                if participant_links[p1] < 5 and participant_links[p2] < 5:
                    links.append({
                        'source': p1,
                        'target': p2,
                        'value': 1
                    })
                    participant_links[p1] += 1
                    participant_links[p2] += 1
    
    return {
        'nodes': nodes,
        'links': links,
        'metadata': {
            'total_participants': len(participants),
            'total_hosts': sum(1 for p in participants.values() if p.host_spaces),
            'total_speakers': sum(1 for p in participants.values() if p.speaker_spaces),
            'total_both': sum(1 for p in participants.values() if p.host_spaces and p.speaker_spaces),
            'visualized_participants': len(nodes),
            'visualized_links': len(links),
            'generated_at': datetime.now().isoformat()
        }
    }

def save_processed_data(participants: Dict[str, ParticipantNode], output_dir: str = None):
    """Save processed data to JSON files"""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save network data
    network_data = generate_network_data(participants)
    network_file = os.path.join(output_dir, 'network_data.json')
    with open(network_file, 'w') as f:
        json.dump(network_data, f, indent=2)
    
    # Save detailed participant data
    participants_file = os.path.join(output_dir, 'participants_data.json')
    with open(participants_file, 'w') as f:
        json.dump([p.to_dict() for p in participants.values()], f, indent=2)
    
    logger.info(f"Saved network data to: {network_file}")
    logger.info(f"Saved detailed participant data to: {participants_file}")

if __name__ == "__main__":
    try:
        # Process the data
        participants = process_participants_data()
        
        # Save the processed data
        save_processed_data(participants)
        
        # Print some statistics
        logger.info("\nStatistics:")
        logger.info(f"Total unique participants: {len(participants)}")
        logger.info(f"Participants who have hosted: {sum(1 for p in participants.values() if p.host_spaces)}")
        logger.info(f"Participants who have spoken: {sum(1 for p in participants.values() if p.speaker_spaces)}")
        logger.info(f"Participants who have done both: {sum(1 for p in participants.values() if p.host_spaces and p.speaker_spaces)}")
        
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}") 