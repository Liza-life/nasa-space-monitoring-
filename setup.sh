#!/bin/bash

# NASA Space Monitoring Platform - Automated Setup Script
# This script automates the initial setup process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "======================================================================"
    echo "  🚀 NASA SPACE MONITORING PLATFORM - SETUP"
    echo "======================================================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

# Main setup process
main() {
    print_header
    
    # Step 1: Check prerequisites
    print_info "Step 1: Checking prerequisites..."
    
    if ! check_command python3; then
        print_error "Python 3 is required. Please install it from https://www.python.org/"
        exit 1
    fi
    
    if ! check_command docker; then
        print_warning "Docker is not installed. Some features will not work."
        print_info "Install Docker from https://www.docker.com/products/docker-desktop"
    fi
    
    if ! check_command git; then
        print_warning "Git is not installed. Version control features will be limited."
    fi
    
    print_success "Prerequisites check complete"
    echo ""
    
    # Step 2: Create directory structure
    print_info "Step 2: Creating directory structure..."
    
    mkdir -p data/{raw,processed,analytics}/{neo,apod,mars,donki}
    mkdir -p data/warehouse
    mkdir -p logs
    mkdir -p notebooks
    mkdir -p tests
    
    print_success "Directory structure created"
    echo ""
    
    # Step 3: Set up Python environment
    print_info "Step 3: Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    print_success "Virtual environment activated"
    echo ""
    
    # Step 4: Install dependencies
    print_info "Step 4: Installing Python dependencies..."
    
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt
    
    print_success "Dependencies installed"
    echo ""
    
    # Step 5: Set up environment variables
    print_info "Step 5: Configuring environment variables..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_warning "Created .env file from template"
        print_warning "IMPORTANT: Edit .env and add your NASA API key!"
        print_info "Get your free API key at: https://api.nasa.gov/"
    else
        print_info ".env file already exists"
    fi
    
    echo ""
    
    # Step 6: Test NASA API connection
    print_info "Step 6: Testing NASA API connection..."
    
    python3 << EOF
import os
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")

try:
    response = requests.get(
        "https://api.nasa.gov/planetary/apod",
        params={"api_key": api_key},
        timeout=10
    )
    if response.status_code == 200:
        print("✅ NASA API connection successful!")
        data = response.json()
        print(f"   Today's APOD: {data.get('title', 'N/A')}")
    else:
        print(f"⚠️  API returned status code: {response.status_code}")
        if api_key == "DEMO_KEY":
            print("   You're using DEMO_KEY. Get your own key at https://api.nasa.gov/")
except Exception as e:
    print(f"❌ API test failed: {e}")
EOF
    
    echo ""
    
    # Step 7: Initialize database
    print_info "Step 7: Initializing DuckDB database..."
    
    python3 << EOF
import duckdb
from pathlib import Path

db_path = Path("data/warehouse/nasa_space.duckdb")
db_path.parent.mkdir(parents=True, exist_ok=True)

conn = duckdb.connect(str(db_path))
conn.execute("""
    CREATE TABLE IF NOT EXISTS fact_asteroid_approaches (
        asteroid_id VARCHAR,
        name VARCHAR,
        close_approach_date TIMESTAMP,
        miss_distance_km DOUBLE,
        miss_distance_lunar DOUBLE,
        relative_velocity_kms DOUBLE,
        diameter_avg_km DOUBLE,
        is_potentially_hazardous BOOLEAN,
        threat_level VARCHAR,
        size_category VARCHAR,
        risk_score DOUBLE,
        days_until_approach INTEGER,
        year INTEGER,
        month INTEGER,
        day INTEGER,
        ingestion_timestamp TIMESTAMP,
        PRIMARY KEY (asteroid_id, close_approach_date)
    )
""")
conn.close()
print("✅ Database initialized successfully")
EOF
    
    echo ""
    
    # Step 8: Run initial data ingestion (optional)
    print_info "Step 8: Would you like to run initial data ingestion? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_info "Running data ingestion..."
        python src/ingestion/neo_ingestion.py
        print_success "Initial data ingestion complete"
        
        print_info "Running data transformation..."
        python src/transformation/neo_transformer.py
        print_success "Data transformation complete"
    else
        print_info "Skipping initial data ingestion"
    fi
    
    echo ""
    
    # Final summary
    print_header
    echo -e "${GREEN}"
    echo "🎉 Setup Complete! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file and add your NASA API key"
    echo "2. Run the dashboard: streamlit run src/dashboard/app.py"
    echo "3. Or start with Docker: docker-compose up -d"
    echo ""
    echo "Useful commands:"
    echo "  • Activate venv: source venv/bin/activate"
    echo "  • Run ingestion: python src/ingestion/neo_ingestion.py"
    echo "  • Run dashboard: streamlit run src/dashboard/app.py"
    echo "  • Start Docker: docker-compose up -d"
    echo "  • View logs: docker-compose logs -f"
    echo ""
    echo "Documentation:"
    echo "  • Quick Start: docs/QUICKSTART.md"
    echo "  • Architecture: docs/ARCHITECTURE.md"
    echo "  • Main README: README.md"
    echo ""
    echo "🚀 Happy space monitoring!"
    echo -e "${NC}"
    
    # Create a setup completion marker
    touch .setup_complete
}

# Run main function
main
