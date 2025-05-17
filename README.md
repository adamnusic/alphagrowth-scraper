# AlphaGrowth Spaces Analysis

A visualization tool that analyzes participation in AlphaGrowth Twitter Spaces, providing insights into hosts, speakers, and overall engagement.

## Features

- **Participation Statistics**: View total participants, hosts, speakers, and spaces
- **Top Participants**: Discover the most active hosts and speakers
- **Interactive Lists**: Filter and sort participants by their roles
- **X Integration**: Direct links to participants' X profiles
- **Responsive Design**: Works on both desktop and mobile devices

## Tech Stack

- Frontend: React with TypeScript, Tailwind CSS
- Backend: Python Flask
- Data Processing: Pandas
- Visualization: D3.js

## Setup

### Prerequisites

- Node.js (v14 or higher)
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/alphagrowth-scraper.git
cd alphagrowth-scraper
```

2. Set up the backend:
```bash
cd alphagrowth-visualizer/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd ../frontend
npm install
```

### Running the Application

1. Start the backend server:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

The application will be available at `http://localhost:3000`

## Data Processing

The application processes data from AlphaGrowth Twitter Spaces, including:
- Participant information
- Host and speaker roles
- Space participation statistics
- X profile links

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 