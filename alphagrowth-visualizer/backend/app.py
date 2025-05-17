from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Paths to data files
data_dir = os.path.join(os.path.dirname(__file__), 'data')
network_data_path = os.path.join(data_dir, 'network_data.json')
participants_data_path = os.path.join(data_dir, 'participants_data.json')

# Load data into memory on startup
try:
    with open(network_data_path, 'r') as f:
        network_data = json.load(f)
        logger.info(f"Loaded network data with {len(network_data.get('nodes', []))} nodes and {len(network_data.get('links', []))} links")
except Exception as e:
    logger.error(f"Error loading network data: {str(e)}")
    network_data = {"nodes": [], "links": []}

try:
    with open(participants_data_path, 'r') as f:
        participants_data = json.load(f)
        logger.info(f"Loaded participants data with {len(participants_data)} participants")
except Exception as e:
    logger.error(f"Error loading participants data: {str(e)}")
    participants_data = []

@app.route('/api/network')
def get_network_data():
    if not isinstance(network_data, dict) or 'nodes' not in network_data or 'links' not in network_data:
        logger.error("Invalid network data format")
        return jsonify({"error": "Invalid network data format"}), 500
    return jsonify(network_data)

@app.route('/api/participants')
def get_participants():
    if not participants_data:
        return jsonify({"error": "No participant data available"}), 500

    # Transform the data to match the frontend's expected format
    transformed_participants = []
    for participant in participants_data:
        # Determine role based on participation
        has_hosted = len(participant['host_spaces']) > 0
        has_spoken = len(participant['speaker_spaces']) > 0
        
        if has_hosted and has_spoken:
            role = 'both'
        elif has_hosted:
            role = 'host'
        else:
            role = 'speaker'
        
        transformed_participant = {
            'name': participant['name'],
            'spaces': participant['total_spaces'],
            'role': role,
            'host_spaces': len(participant['host_spaces']),
            'speaker_spaces': len(participant['speaker_spaces']),
            'twitter': participant.get('twitter')  # Add Twitter link
        }
        transformed_participants.append(transformed_participant)
        
        # Log the first few participants for debugging
        if len(transformed_participants) <= 5:
            logger.info(f"Transformed participant: {transformed_participant}")

    # Log role distribution
    role_counts = {
        'host': sum(1 for p in transformed_participants if p['role'] == 'host'),
        'speaker': sum(1 for p in transformed_participants if p['role'] == 'speaker'),
        'both': sum(1 for p in transformed_participants if p['role'] == 'both')
    }
    logger.info(f"Role distribution: {role_counts}")

    return jsonify(transformed_participants)

@app.route('/api/participants/<participant_id>')
def get_participant_details(participant_id):
    if not isinstance(participants_data, list):
        logger.error("Invalid participants data format")
        return jsonify({"error": "Invalid participants data format"}), 500
    
    participant = next((p for p in participants_data if p.get('id') == participant_id), None)
    if participant:
        return jsonify(participant)
    return jsonify({'error': 'Participant not found'}), 404

@app.route('/api/stats')
def get_stats():
    if not participants_data:
        return jsonify({"error": "No participant data available"}), 500

    # Calculate statistics
    total_participants = len(participants_data)
    total_hosts = sum(1 for p in participants_data if p['host_spaces'])
    total_speakers = sum(1 for p in participants_data if p['speaker_spaces'])
    total_both = sum(1 for p in participants_data if p['host_spaces'] and p['speaker_spaces'])

    # Calculate total unique spaces
    all_spaces = set()
    for participant in participants_data:
        all_spaces.update(participant['host_spaces'])
        all_spaces.update(participant['speaker_spaces'])
    total_spaces = len(all_spaces)

    # Calculate average participants per space
    space_participants = defaultdict(set)
    for participant in participants_data:
        for space in participant['host_spaces'] + participant['speaker_spaces']:
            space_participants[space].add(participant['id'])
    average_participants = sum(len(participants) for participants in space_participants.values()) / total_spaces if total_spaces > 0 else 0

    # Find most active host and speaker
    most_active_host = max(participants_data, key=lambda x: len(x['host_spaces']))
    most_active_speaker = max(participants_data, key=lambda x: len(x['speaker_spaces']))

    stats = {
        'total_participants': total_participants,
        'total_hosts': total_hosts,
        'total_speakers': total_speakers,
        'total_both': total_both,
        'total_spaces': total_spaces,
        'average_participants_per_space': average_participants,
        'most_active_host': {
            'name': most_active_host['name'],
            'spaces': len(most_active_host['host_spaces'])
        },
        'most_active_speaker': {
            'name': most_active_speaker['name'],
            'spaces': len(most_active_speaker['speaker_spaces'])
        }
    }

    return jsonify(stats)

@app.route('/')
def index():
    return "AlphaGrowth Network API is running."

if __name__ == '__main__':
    app.run(debug=True, port=5002) 