# Action Item 2: Setup and Configure FaultExplainer

## Overview
This document guides you through setting up the FaultExplainer system for fault detection and diagnosis.

## Prerequisites
- Python 3.7+
- Node.js (for frontend)
- Yarn package manager

## Setup Steps
1. **Backend Setup**
   ```bash
   cd FaultExplainer-main/backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Frontend Setup**
   ```bash
   cd ../frontend
   yarn install
   ```

3. **Configuration**
   - Create a `.env` file in the backend directory
   - Add your LLM API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

## Running the Application
1. Start backend server:
   ```bash
   cd backend
   uvicorn app:app --reload
   ```
   The API will be available at `http://localhost:8000`

2. Start frontend development server:
   ```bash
   cd frontend
   yarn dev
   ```
   The web interface will be available at `http://localhost:3000`

## Integration with TEP Simulator
1. **Data Format**
   - Ensure your TEP simulation data is in CSV format
   - Required columns: timestamp, variable names matching TEP standard

2. **API Endpoints**
   - `POST /api/analyze`: Upload and analyze TEP data
   - `GET /api/results`: Get analysis results

## Testing the Setup
1. **Backend Test**
   ```bash
   cd backend
   python -m pytest
   ```

2. **Frontend Test**
   ```bash
   cd frontend
   yarn test
   ```

## Troubleshooting
- **Port Conflicts**: Change ports in `backend/main.py` or frontend config if needed
- **API Connection**: Ensure CORS is properly configured
- **LLM Errors**: Verify your API key and quota

## Next Steps
- Proceed to Action Item 3 for SensorSCAN integration
- Document any integration issues
- Create test cases for different fault scenarios
