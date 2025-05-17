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

def load_json_data(filename):
    try:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        file_path = os.path.join(data_dir, filename)
        
        if not os.path.exists(file_path):
            logger.error(f"Data file not found: {file_path}")
            return None
            
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filename}: {str(e)}")
        return None

@app.route('/api/network')
def get_network():
    network = load_json_data('network_data.json')
    if not network:
        return jsonify({"error": "No network data available"}), 500
    return jsonify(network)

@app.route('/api/participants')
def get_participants():
    participants = load_json_data('participants_data.json')
    if not participants:
        return jsonify({"error": "No participant data available"}), 500
    return jsonify(participants)

@app.route('/api/participants/<participant_id>')
def get_participant_details(participant_id):
    participants = load_json_data('participants_data.json')
    if not participants:
        return jsonify({"error": "No participant data available"}), 500
    
    participant = next((p for p in participants if p.get('id') == participant_id), None)
    if participant:
        return jsonify(participant)
    return jsonify({'error': 'Participant not found'}), 404

@app.route('/api/stats')
def get_stats():
    participants = load_json_data('participants_data.json')
    if not participants:
        return jsonify({"error": "No participant data available"}), 500

    # Calculate stats
    total_participants = len(participants)
    total_hosts = sum(1 for p in participants if p['role'] == 'host')
    total_speakers = sum(1 for p in participants if p['role'] == 'speaker')
    total_both = sum(1 for p in participants if p['role'] == 'both')
    total_spaces = sum(p['spaces'] for p in participants)
    
    # Find most active host and speaker
    hosts = [p for p in participants if p['role'] in ['host', 'both']]
    speakers = [p for p in participants if p['role'] in ['speaker', 'both']]
    
    most_active_host = max(hosts, key=lambda x: x['spaces']) if hosts else {'name': 'N/A', 'spaces': 0}
    most_active_speaker = max(speakers, key=lambda x: x['spaces']) if speakers else {'name': 'N/A', 'spaces': 0}

    return jsonify({
        'total_participants': total_participants,
        'total_hosts': total_hosts,
        'total_speakers': total_speakers,
        'total_both': total_both,
        'total_spaces': total_spaces,
        'average_participants_per_space': total_spaces / total_participants if total_participants > 0 else 0,
        'most_active_host': {
            'name': most_active_host['name'],
            'spaces': most_active_host['spaces']
        },
        'most_active_speaker': {
            'name': most_active_speaker['name'],
            'spaces': most_active_speaker['spaces']
        }
    })

@app.route('/')
def index():
    return "AlphaGrowth Network API is running."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000) 