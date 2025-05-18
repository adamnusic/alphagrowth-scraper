from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import logging
import traceback
from collections import defaultdict
from datetime import datetime
import pandas as pd

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
        "supports_credentials": True,
        "max_age": 3600
    }
})

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://delicate-marshmallow-d974fc.netlify.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

def get_data_dir():
    """Get the absolute path to the data directory."""
    # Get the directory where app.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define all possible data directory locations in order of preference
    possible_data_dirs = [
        os.path.join(current_dir, 'data'),  # Local development
        os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'data'),  # Parent directory data
        '/opt/render/project/src/alphagrowth-visualizer/backend/data',  # Render deployment backend data
        '/opt/render/project/src/alphagrowth-visualizer/data',  # Render deployment root data
        '/opt/render/project/src/data',  # Root data directory
        os.path.join(os.getcwd(), 'data'),  # Current working directory data
    ]
    
    # Log all possible locations and their contents
    logger.info("Checking possible data directory locations:")
    for dir_path in possible_data_dirs:
        logger.info(f"Checking: {dir_path}")
        if os.path.exists(dir_path):
            try:
                contents = os.listdir(dir_path)
                logger.info(f"Found data directory at: {dir_path}")
                logger.info(f"Contents: {contents}")
                
                # Verify essential files exist
                required_files = ['participants_data.json', 'network_data.json', 'total_spaces.txt']
                missing_files = [f for f in required_files if f not in contents]
                
                if missing_files:
                    logger.warning(f"Directory {dir_path} is missing required files: {missing_files}")
                    continue
                    
                return dir_path
            except Exception as e:
                logger.error(f"Error checking directory {dir_path}: {str(e)}")
                continue
        else:
            logger.info(f"Directory not found: {dir_path}")
    
    # If no valid data directory found, raise an error with clear instructions
    error_msg = """
    No valid data directory found! Please ensure one of these directories exists and contains the required files:
    - /opt/render/project/src/alphagrowth-visualizer/backend/data
    - /opt/render/project/src/alphagrowth-visualizer/data
    - /opt/render/project/src/data
    
    Required files:
    - participants_data.json
    - network_data.json
    - total_spaces.txt
    """
    logger.error(error_msg)
    raise FileNotFoundError(error_msg)

def load_json_data(filename):
    """Load JSON data from the data directory."""
    try:
        data_dir = get_data_dir()
        file_path = os.path.join(data_dir, filename)
        
        logger.info(f"Attempting to load: {file_path}")
        
        if not os.path.exists(file_path):
            error_msg = f"Required file not found: {filename}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        with open(file_path, 'r') as f:
            data = json.load(f)
            
            # Validate data structure
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON string from {filename}: {str(e)}")
                    raise
                    
            if not isinstance(data, list):
                error_msg = f"Data from {filename} is not a list: {type(data)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            logger.info(f"Successfully loaded {filename} with {len(data)} items")
            return data
            
    except Exception as e:
        logger.error(f"Error loading {filename}: {str(e)}")
        logger.error(traceback.format_exc())
        raise

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

def get_total_spaces():
    """Get the total number of spaces from total_spaces.txt."""
    try:
        data_dir = get_data_dir()
        file_path = os.path.join(data_dir, 'total_spaces.txt')
        
        logger.info(f"Looking for total_spaces.txt at: {file_path}")
        if not os.path.exists(file_path):
            logger.error(f"total_spaces.txt not found at: {file_path}")
            # Try to find the file in the repository
            repo_root = '/opt/render/project/src'
            for root, dirs, files in os.walk(repo_root):
                if 'total_spaces.txt' in files:
                    found_path = os.path.join(root, 'total_spaces.txt')
                    logger.info(f"Found total_spaces.txt in repository at: {found_path}")
                    file_path = found_path
                    break
            else:
                logger.error(f"Could not find total_spaces.txt anywhere in the repository")
                return None
            
        with open(file_path, 'r') as f:
            total_spaces = int(f.read().strip())
            logger.info(f"Total spaces from total_spaces.txt: {total_spaces}")
            return total_spaces
            
    except Exception as e:
        logger.error(f"Error reading total_spaces.txt: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def get_last_run_date():
    """Get the date of the most recent data collection."""
    try:
        data_dir = get_data_dir()
        logger.info(f"Looking for participants files in: {data_dir}")
        
        # List all files in the data directory
        all_files = os.listdir(data_dir)
        logger.info(f"All files in data directory: {all_files}")
        
        # Look for both participants_*.csv and participants.csv
        participants_files = [f for f in all_files if (f.startswith('participants_') and f.endswith('.csv')) or f == 'participants.csv']
        logger.info(f"Found participants CSV files: {participants_files}")
        
        if not participants_files:
            logger.warning("No participants CSV files found!")
            return None
            
        # Get the latest file
        latest_file = sorted(participants_files)[-1]
        logger.info(f"Latest participants file: {latest_file}")
        
        # Extract date from filename (participants_YYYYMMDD.csv)
        if latest_file.startswith('participants_'):
            date_str = latest_file.split('_')[1].split('.')[0]
            # Convert to readable format
            date = datetime.strptime(date_str, '%Y%m%d')
            return date.strftime('%B %d, %Y')
        else:
            # If it's just participants.csv, use its modification time
            file_path = os.path.join(data_dir, latest_file)
            mod_time = os.path.getmtime(file_path)
            date = datetime.fromtimestamp(mod_time)
            return date.strftime('%B %d, %Y')
            
    except Exception as e:
        logger.error(f"Error getting last run date: {str(e)}")
        logger.error(traceback.format_exc())
        return None

@app.route('/api/stats')
def get_stats():
    try:
        data_dir = get_data_dir()
        stats_file = os.path.join(data_dir, 'stats.json')
        
        # Try to load pre-calculated stats
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
                    logger.info(f"Loaded pre-calculated stats from {stats_file}")
                    return jsonify(stats)
            except Exception as e:
                logger.error(f"Error loading stats.json: {str(e)}")
                # Continue with calculation if file is corrupted
        
        # If stats.json doesn't exist or is corrupted, calculate stats
        participants = load_json_data('participants_data.json')
        if not participants:
            return jsonify({"error": "No participant data available"}), 500

        # Get total spaces from total_spaces.txt
        total_spaces = get_total_spaces()
        if total_spaces is None:
            return jsonify({"error": "Could not read total spaces from total_spaces.txt"}), 500

        # Get last run date
        last_run_date = get_last_run_date()

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
        total_host_spaces = sum(p['host_spaces'] for p in cleaned_participants)
        total_speaker_spaces = sum(p['speaker_spaces'] for p in cleaned_participants)
        
        # Find most active host and speaker
        most_active_host = max(hosts, key=lambda x: x['host_spaces']) if hosts else {'name': 'N/A', 'host_spaces': 0}
        most_active_speaker = max(speakers, key=lambda x: x['speaker_spaces']) if speakers else {'name': 'N/A', 'speaker_spaces': 0}

        # Calculate average participants per space from participants.csv
        participants_file = os.path.join(data_dir, 'participants.csv')
        if os.path.exists(participants_file):
            try:
                # Read the first line to get total rows
                with open(participants_file, 'r') as f:
                    total_rows = sum(1 for _ in f) - 1  # Subtract header row
                
                # Calculate average
                average_participants_per_space = total_rows / total_spaces if total_spaces > 0 else 0
                logger.info(f"Calculated average participants per space: {average_participants_per_space:.2f}")
            except Exception as e:
                logger.error(f"Error calculating average participants per space: {str(e)}")
                average_participants_per_space = 0
        else:
            average_participants_per_space = 0
            logger.warning("participants.csv not found, using default average of 0")

        # Prepare stats
        stats = {
            'total_participants': total_participants,
            'total_hosts': total_hosts,
            'total_speakers': total_speakers,
            'total_both': total_both,
            'total_spaces': total_spaces,
            'total_host_spaces': total_host_spaces,
            'total_speaker_spaces': total_speaker_spaces,
            'average_participants_per_space': round(average_participants_per_space, 2),
            'most_active_host': {
                'name': most_active_host['name'],
                'spaces': most_active_host['host_spaces']
            },
            'most_active_speaker': {
                'name': most_active_speaker['name'],
                'spaces': most_active_speaker['speaker_spaces']
            },
            'last_run_date': last_run_date
        }

        # Save stats to file for future use
        try:
            with open(stats_file, 'w') as f:
                json.dump(stats, f)
            logger.info(f"Saved stats to {stats_file}")
        except Exception as e:
            logger.error(f"Error saving stats to file: {str(e)}")

        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error in get_stats: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/last-run')
def get_last_run():
    """Get the date of the most recent data collection."""
    try:
        last_run_date = get_last_run_date()
        if last_run_date is None:
            return jsonify({"error": "Could not determine last run date"}), 500
        return jsonify({"last_run_date": last_run_date})
    except Exception as e:
        logger.error(f"Error in get_last_run: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@app.route('/')
def index():
    return "AlphaGrowth Network API is running."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000))) 