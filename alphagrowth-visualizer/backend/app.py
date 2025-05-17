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

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://delicate-marshmallow-d974fc.netlify.app",
            "http://localhost:5173"  # For local development
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False,
        "max_age": 3600
    }
})

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://delicate-marshmallow-d974fc.netlify.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

def get_data_dir():
    """Get the absolute path to the data directory."""
    # Get the directory where app.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List all possible data directory locations
    possible_data_dirs = [
        os.path.join(current_dir, 'data'),  # Local development
        os.path.join('/opt/render/project/src/alphagrowth-visualizer/backend/data'),  # Render deployment
        os.path.join('/opt/render/project/src/data'),  # Root data directory
        os.path.join(current_dir, '..', 'data'),  # Parent directory data
        os.path.join(os.getcwd(), 'data')  # Current working directory data
    ]
    
    # Log all possible locations
    logger.info("Checking possible data directory locations:")
    for dir_path in possible_data_dirs:
        logger.info(f"Checking: {dir_path}")
        if os.path.exists(dir_path):
            logger.info(f"Found data directory at: {dir_path}")
            logger.info(f"Contents: {os.listdir(dir_path)}")
            return dir_path
        else:
            logger.info(f"Directory not found: {dir_path}")
    
    # If no data directory found, return the default location
    default_dir = os.path.join(current_dir, 'data')
    logger.info(f"No data directory found, using default: {default_dir}")
    return default_dir

def load_json_data(filename):
    """Load JSON data from the data directory."""
    try:
        data_dir = get_data_dir()
        file_path = os.path.join(data_dir, filename)
        
        logger.info(f"Attempting to load: {file_path}")
        logger.info(f"File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            # Try to find the file in the repository
            repo_root = '/opt/render/project/src'
            for root, dirs, files in os.walk(repo_root):
                if filename in files:
                    found_path = os.path.join(root, filename)
                    logger.info(f"Found file in repository at: {found_path}")
                    file_path = found_path
                    break
            else:
                logger.error(f"Could not find {filename} anywhere in the repository")
                return None
            
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Ensure we're returning a list
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON string from {filename}")
                    return None
            if not isinstance(data, list):
                logger.error(f"Data from {filename} is not a list: {type(data)}")
                return None
            logger.info(f"Successfully loaded {filename}")
            return data
            
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
        
        # Clean and validate each participant
        cleaned_participants = []
        for participant in participants:
            try:
                # Ensure all required fields are present and valid
                cleaned = {
                    'id': str(participant.get('id', '')),
                    'name': str(participant.get('name', '')),
                    'role': str(participant.get('role', 'speaker')),
                    'spaces': int(participant.get('spaces', 0)),
                    'speaker_spaces': int(participant.get('speaker_spaces', 0)),
                    'twitter': str(participant.get('twitter', '')) if participant.get('twitter') else None
                }
                
                # Calculate host_spaces
                cleaned['host_spaces'] = cleaned['spaces'] - cleaned['speaker_spaces']
                
                # Validate role
                if cleaned['role'] not in ['host', 'speaker', 'both']:
                    cleaned['role'] = 'both' if cleaned['host_spaces'] > 0 and cleaned['speaker_spaces'] > 0 else \
                                    'host' if cleaned['host_spaces'] > 0 else 'speaker'
                
                cleaned_participants.append(cleaned)
            except (ValueError, TypeError) as e:
                logger.error(f"Error cleaning participant data: {str(e)}")
                continue
        
        # Log the first few participants for debugging
        logger.info(f"First 3 participants: {cleaned_participants[:3]}")
        logger.info(f"Total participants: {len(cleaned_participants)}")
        
        return jsonify(cleaned_participants)
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

        # Clean and validate participants first
        cleaned_participants = []
        for participant in participants:
            try:
                cleaned = {
                    'id': str(participant.get('id', '')),
                    'name': str(participant.get('name', '')),
                    'role': str(participant.get('role', 'speaker')),
                    'spaces': int(participant.get('spaces', 0)),
                    'speaker_spaces': int(participant.get('speaker_spaces', 0)),
                    'twitter': str(participant.get('twitter', '')) if participant.get('twitter') else None
                }
                
                # Calculate host_spaces
                cleaned['host_spaces'] = cleaned['spaces'] - cleaned['speaker_spaces']
                
                # Validate role
                if cleaned['role'] not in ['host', 'speaker', 'both']:
                    cleaned['role'] = 'both' if cleaned['host_spaces'] > 0 and cleaned['speaker_spaces'] > 0 else \
                                    'host' if cleaned['host_spaces'] > 0 else 'speaker'
                
                cleaned_participants.append(cleaned)
            except (ValueError, TypeError) as e:
                logger.error(f"Error cleaning participant data: {str(e)}")
                continue

        # Calculate stats
        total_participants = len(cleaned_participants)
        
        # Count unique roles
        hosts = [p for p in cleaned_participants if p['role'] in ['host', 'both']]
        speakers = [p for p in cleaned_participants if p['role'] in ['speaker', 'both']]
        both = [p for p in cleaned_participants if p['role'] == 'both']
        
        total_hosts = len(hosts)
        total_speakers = len(speakers)
        total_both = len(both)
        
        # Calculate spaces
        total_spaces = sum(p['spaces'] for p in cleaned_participants)
        total_host_spaces = sum(p['host_spaces'] for p in cleaned_participants)
        total_speaker_spaces = sum(p['speaker_spaces'] for p in cleaned_participants)
        
        # Find most active host and speaker
        most_active_host = max(hosts, key=lambda x: x['host_spaces']) if hosts else {'name': 'N/A', 'host_spaces': 0}
        most_active_speaker = max(speakers, key=lambda x: x['speaker_spaces']) if speakers else {'name': 'N/A', 'speaker_spaces': 0}

        # Log stats for debugging
        logger.info(f"Stats calculation:")
        logger.info(f"Total participants: {total_participants}")
        logger.info(f"Total hosts: {total_hosts}")
        logger.info(f"Total speakers: {total_speakers}")
        logger.info(f"Total both: {total_both}")
        logger.info(f"Total spaces: {total_spaces}")
        logger.info(f"Total host spaces: {total_host_spaces}")
        logger.info(f"Total speaker spaces: {total_speaker_spaces}")
        
        # Log some sample data
        logger.info("Sample participants:")
        for p in cleaned_participants[:5]:
            logger.info(f"{p['name']}: role={p['role']}, spaces={p['spaces']}, host_spaces={p['host_spaces']}, speaker_spaces={p['speaker_spaces']}")

        return jsonify({
            'total_participants': total_participants,
            'total_hosts': total_hosts,
            'total_speakers': total_speakers,
            'total_both': total_both,
            'total_spaces': total_spaces,
            'total_host_spaces': total_host_spaces,
            'total_speaker_spaces': total_speaker_spaces,
            'average_participants_per_space': total_spaces / total_participants if total_participants > 0 else 0,
            'most_active_host': {
                'name': most_active_host['name'],
                'spaces': most_active_host['host_spaces']
            },
            'most_active_speaker': {
                'name': most_active_speaker['name'],
                'spaces': most_active_speaker['speaker_spaces']
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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000))) 