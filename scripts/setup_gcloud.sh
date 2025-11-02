#!/bin/bash

# Usage: bash scripts/setup_gcloud.sh
# This script logs you into Google Cloud, sets the active project,
# enables required APIs, and verifies configuration before deployment.
# It also checks if all backend services are running before proceeding.

# Color definitions
RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
BLUE=$(tput setaf 4)
CYAN=$(tput setaf 6)
RESET=$(tput sgr0)

# Header
echo "${CYAN}========================================${RESET}"
echo "${CYAN}   Google Cloud Setup & Configuration${RESET}"
echo "${CYAN}========================================${RESET}"
echo ""

# Function to print success message
print_success() {
    echo "${GREEN}✅ $1${RESET}"
}

# Function to print error message
print_error() {
    echo "${RED}❌ $1${RESET}"
}

# Function to print info message
print_info() {
    echo "${BLUE}ℹ️  $1${RESET}"
}

# Function to print warning message
print_warning() {
    echo "${YELLOW}⚠️  $1${RESET}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Check for gcloud CLI
echo "${BLUE}🔍 Checking for Google Cloud CLI...${RESET}"
if ! command_exists gcloud; then
    print_error "Google Cloud CLI (gcloud) is not installed."
    echo ""
    echo "Please install it from: ${CYAN}https://cloud.google.com/sdk/docs/install${RESET}"
    echo ""
    exit 1
fi
print_success "Google Cloud CLI found."
echo ""

# 2. Check if backend services are running
echo "${BLUE}🔍 Checking if backend services are running...${RESET}"

check_port() {
    local port=$1
    local service_name=$2
    
    if command_exists netstat; then
        if netstat -ano | grep ":$port " | grep "LISTENING" > /dev/null 2>&1; then
            print_success "$service_name is running on port $port"
            return 0
        else
            print_warning "$service_name is NOT running on port $port"
            return 1
        fi
    elif command_exists lsof; then
        if lsof -i :$port > /dev/null 2>&1; then
            print_success "$service_name is running on port $port"
            return 0
        else
            print_warning "$service_name is NOT running on port $port"
            return 1
        fi
    else
        print_info "Cannot check port $port (netstat/lsof not available)"
        return 2
    fi
}

# Check all required services
services_ok=true
check_port 8000 "Manager Service" || services_ok=false
check_port 8001 "Search Agent" || services_ok=false
check_port 8002 "Sentiment Agent" || services_ok=false
check_port 8003 "Trends Agent" || services_ok=false

if [ "$services_ok" = false ]; then
    echo ""
    print_warning "Some backend services are not running!"
    echo ""
    echo "To start all services, run:"
    echo "  ${CYAN}bash test_services.sh${RESET}"
    echo ""
    read -p "Do you want to continue with GCloud setup anyway? (y/n): " continue_setup
    if [[ ! "$continue_setup" =~ ^[Yy]$ ]]; then
        print_info "Setup cancelled. Please start your services first."
        exit 0
    fi
else
    print_success "All backend services are running!"
fi
echo ""

# 3. Authenticate User
echo "${BLUE}🔑 Logging into Google Cloud...${RESET}"
echo "   (This will open a browser window for authentication)"
echo ""

if gcloud auth login; then
    print_success "Authentication successful."
else
    print_error "Authentication failed."
    exit 1
fi
echo ""

# 4. Set Project
echo "${BLUE}📦 Setting up Google Cloud project...${RESET}"

# Check if a project is already set
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)

if [ -n "$CURRENT_PROJECT" ] && [ "$CURRENT_PROJECT" != "(unset)" ]; then
    print_info "Current project: ${CYAN}$CURRENT_PROJECT${RESET}"
    read -p "Use this project? (y/n): " use_current
    if [[ "$use_current" =~ ^[Yy]$ ]]; then
        PROJECT_ID="$CURRENT_PROJECT"
    else
        read -p "Enter your Google Cloud project ID: " PROJECT_ID
    fi
else
    read -p "Enter your Google Cloud project ID: " PROJECT_ID
fi

# Validate project ID is not empty
if [ -z "$PROJECT_ID" ]; then
    print_error "Project ID cannot be empty."
    exit 1
fi

# Set the project
if gcloud config set project "$PROJECT_ID"; then
    print_success "Active Project: ${CYAN}$PROJECT_ID${RESET}"
else
    print_error "Failed to set project."
    exit 1
fi
echo ""

# 5. Enable Required APIs
echo "${BLUE}⚙️  Enabling required Google Cloud services...${RESET}"
echo "   (This may take a few minutes)"
echo ""

REQUIRED_APIS=(
    "run.googleapis.com"
    "artifactregistry.googleapis.com"
    "cloudbuild.googleapis.com"
    "compute.googleapis.com"
    "storage.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    echo "   Enabling ${CYAN}$api${RESET}..."
done
echo ""

if gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    compute.googleapis.com \
    storage.googleapis.com; then
    print_success "All required APIs enabled successfully."
else
    print_error "Failed to enable some APIs."
    exit 1
fi
echo ""

# 6. Verify Configuration
echo "${BLUE}🔍 Verifying configuration...${RESET}"
echo ""

# Get active account
ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -n 1)
if [ -n "$ACTIVE_ACCOUNT" ]; then
    print_success "Active Account: ${CYAN}$ACTIVE_ACCOUNT${RESET}"
else
    print_error "No active account found."
    exit 1
fi

# Get active project
ACTIVE_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ -n "$ACTIVE_PROJECT" ] && [ "$ACTIVE_PROJECT" != "(unset)" ]; then
    print_success "Active Project: ${CYAN}$ACTIVE_PROJECT${RESET}"
else
    print_error "No active project configured."
    exit 1
fi

# Get project number
PROJECT_NUMBER=$(gcloud projects describe "$ACTIVE_PROJECT" --format="value(projectNumber)" 2>/dev/null)
if [ -n "$PROJECT_NUMBER" ]; then
    print_success "Project Number: ${CYAN}$PROJECT_NUMBER${RESET}"
fi

# Get default region (if set)
DEFAULT_REGION=$(gcloud config get-value compute/region 2>/dev/null)
if [ -n "$DEFAULT_REGION" ] && [ "$DEFAULT_REGION" != "(unset)" ]; then
    print_info "Default Region: ${CYAN}$DEFAULT_REGION${RESET}"
else
    print_warning "No default region set. You may want to set one using:"
    echo "   ${CYAN}gcloud config set compute/region us-central1${RESET}"
fi

echo ""

# 7. Additional Health Checks
echo "${BLUE}🏥 Running additional health checks...${RESET}"
echo ""

# Check if Docker is installed (needed for building containers)
if command_exists docker; then
    print_success "Docker is installed"
    
    # Check if Docker daemon is running
    if docker info >/dev/null 2>&1; then
        print_success "Docker daemon is running"
    else
        print_warning "Docker is installed but daemon is not running"
        echo "   Start Docker Desktop or Docker service before deployment"
    fi
else
    print_warning "Docker is not installed"
    echo "   Docker is required for building container images"
    echo "   Install from: ${CYAN}https://docs.docker.com/get-docker/${RESET}"
fi

# Check Python version
if command_exists python; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    print_success "Python is installed (version $PYTHON_VERSION)"
elif command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python3 is installed (version $PYTHON_VERSION)"
else
    print_warning "Python is not found in PATH"
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    print_success "Python virtual environment found (venv/)"
else
    print_info "No virtual environment found. You may want to create one:"
    echo "   ${CYAN}python -m venv venv${RESET}"
fi

echo ""

# 8. Final Confirmation
echo "${GREEN}========================================${RESET}"
echo "${GREEN}🎉 Google Cloud setup complete!${RESET}"
echo "${GREEN}========================================${RESET}"
echo ""
echo "${CYAN}Configuration Summary:${RESET}"
echo "  Account:  ${CYAN}$ACTIVE_ACCOUNT${RESET}"
echo "  Project:  ${CYAN}$ACTIVE_PROJECT${RESET}"
echo "  APIs:     ${GREEN}Enabled and Ready${RESET}"
echo ""

if [ "$services_ok" = true ]; then
    echo "${GREEN}✅ Backend services are running${RESET}"
else
    echo "${YELLOW}⚠️  Some backend services may not be running${RESET}"
    echo "   Start them with: ${CYAN}bash test_services.sh${RESET}"
fi

echo ""
echo "${CYAN}Next Steps:${RESET}"
echo "  1. Ensure all backend services are running"
echo "  2. Configure your deployment settings in ${CYAN}scripts/deploy_all.sh${RESET}"
echo "  3. Run deployment: ${GREEN}bash scripts/deploy_all.sh${RESET}"
echo ""
echo "${BLUE}For more info:${RESET}"
echo "  - GCP Console: ${CYAN}https://console.cloud.google.com/home/dashboard?project=$ACTIVE_PROJECT${RESET}"
echo "  - Cloud Run:   ${CYAN}https://console.cloud.google.com/run?project=$ACTIVE_PROJECT${RESET}"
echo ""

# Make this script executable once using:
# chmod +x scripts/setup_gcloud.sh
