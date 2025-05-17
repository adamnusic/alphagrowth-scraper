from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import logging
import traceback
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def load_json_data(filename):
    try:
        # Try multiple possible paths
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'data', filename),  # Local development
            os.path.join('/opt/render/project/src', 'data', filename),   # Render deployment
            os.path.join('/opt/render/project/src/alphagrowth-visualizer/backend/data', filename),  # Render backend
            os.path.join(os.getcwd(), 'data', filename),                 # Current directory
            os.path.join('/opt/render/project/src/alphagrowth-visualizer/data', filename)  # Render visualizer
        ]
        
        # Debug logging
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Looking for file in possible paths: {possible_paths}")
        
        # List contents of important directories
        for dir_path in [
            '/opt/render/project/src',
            '/opt/render/project/src/alphagrowth-visualizer',
            '/opt/render/project/src/alphagrowth-visualizer/backend',
            '/opt/render/project/src/alphagrowth-visualizer/backend/data',
            os.path.join(os.getcwd(), 'data')
        ]:
            if os.path.exists(dir_path):
                logger.info(f"Contents of {dir_path}: {os.listdir(dir_path)}")
            else:
                logger.info(f"Directory not found: {dir_path}")
        
        for file_path in possible_paths:
            if os.path.exists(file_path):
                logger.info(f"Found file at: {file_path}")
                logger.info(f"File permissions: {oct(os.stat(file_path).st_mode)[-3:]}")
                logger.info(f"File size: {os.path.getsize(file_path)} bytes")
                
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        logger.info(f"Successfully loaded {filename} with {len(data) if isinstance(data, list) else 'unknown'} items")
                        return data
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in {filename}: {str(e)}")
                    continue
            else:
                logger.info(f"File not found at: {file_path}")
        
        logger.error(f"Could not find {filename} in any of the possible paths")
        return None
    except Exception as e:
        logger.error(f"Error loading {filename}: {str(e)}")
        logger.error(traceback.format_exc())
        return None

@app.route('/api/network')
def get_network():
    try:
        network = load_json_data('network_data.json')
        if not network:
            return jsonify({"error": "No network data available"}), 500
        return jsonify(network)
    except Exception as e:
        logger.error(f"Error in get_network: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/participants')
def get_participants():
    try:
        participants = load_json_data('participants_data.json')
        if not participants:
            return jsonify({"error": "No participant data available"}), 500
        return jsonify(participants)
    except Exception as e:
        logger.error(f"Error in get_participants: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

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
    try:
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
    except Exception as e:
        logger.error(f"Error in get_stats: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@app.route('/')
def index():
    return "AlphaGrowth Network API is running."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000) 