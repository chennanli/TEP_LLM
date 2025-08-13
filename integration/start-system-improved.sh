#!/bin/bash

# TEP Integration - Improved System Startup Script
# Demonstrates best practices for shell scripts with virtual environments

set -euo pipefail  # Exit on error, undefined vars, pipe failures
IFS=$'\n\t'       # Secure Internal Field Separator

# =============================================================================
# CONFIGURATION AND CONSTANTS
# =============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
readonly VENV_NAME="${VENV_NAME:-tep_env}"
readonly BACKEND_PORT="${BACKEND_PORT:-8000}"
readonly FRONTEND_PORT="${FRONTEND_PORT:-5173}"
readonly LOG_FILE="${SCRIPT_DIR}/startup.log"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Process tracking
BACKEND_PID=""
FRONTEND_PID=""

# =============================================================================
# LOGGING AND OUTPUT FUNCTIONS
# =============================================================================

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}ℹ️  $*${NC}" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $*${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $*${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $*${NC}" | tee -a "$LOG_FILE"
}

# =============================================================================
# VIRTUAL ENVIRONMENT FUNCTIONS
# =============================================================================

find_virtual_environment() {
    local venv_paths=(
        "$PROJECT_ROOT/$VENV_NAME"           # Parent directory
        "$SCRIPT_DIR/$VENV_NAME"             # Current directory
        "$HOME/.virtualenvs/$VENV_NAME"      # Global virtualenvs
        "./$VENV_NAME"                       # Relative path
    )
    
    for path in "${venv_paths[@]}"; do
        if [[ -d "$path" ]]; then
            echo "$path"
            return 0
        fi
    done
    
    return 1
}

get_activation_script() {
    local venv_path="$1"
    
    # Cross-platform activation script detection
    if [[ -f "$venv_path/bin/activate" ]]; then
        echo "$venv_path/bin/activate"  # Unix/Linux/macOS
    elif [[ -f "$venv_path/Scripts/activate" ]]; then
        echo "$venv_path/Scripts/activate"  # Windows
    else
        return 1
    fi
}

activate_virtual_environment() {
    info "Searching for virtual environment '$VENV_NAME'..."
    
    local venv_path
    if ! venv_path=$(find_virtual_environment); then
        error "Virtual environment '$VENV_NAME' not found in any of these locations:"
        error "  - $PROJECT_ROOT/$VENV_NAME"
        error "  - $SCRIPT_DIR/$VENV_NAME"
        error "  - $HOME/.virtualenvs/$VENV_NAME"
        error "  - ./$VENV_NAME"
        error ""
        error "Please create the virtual environment or set VENV_NAME environment variable"
        return 1
    fi
    
    local activate_script
    if ! activate_script=$(get_activation_script "$venv_path"); then
        error "Activation script not found in $venv_path"
        error "Expected: $venv_path/bin/activate or $venv_path/Scripts/activate"
        return 1
    fi
    
    info "Found virtual environment at: $venv_path"
    info "Activating virtual environment..."
    
    # Source the activation script
    # shellcheck source=/dev/null
    if ! source "$activate_script"; then
        error "Failed to activate virtual environment"
        return 1
    fi
    
    # Verify activation worked
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        error "Virtual environment activation failed - VIRTUAL_ENV not set"
        return 1
    fi
    
    # Verify Python is from the virtual environment
    local python_path
    python_path=$(which python 2>/dev/null || echo "")
    if [[ "$python_path" != "$VIRTUAL_ENV"* ]]; then
        warning "Python may not be from virtual environment"
        warning "Expected: $VIRTUAL_ENV/bin/python or $VIRTUAL_ENV/Scripts/python"
        warning "Found: $python_path"
    fi
    
    success "Virtual environment activated successfully"
    info "Virtual environment: $VIRTUAL_ENV"
    info "Python version: $(python --version 2>&1)"
    
    return 0
}

# =============================================================================
# CLEANUP AND SIGNAL HANDLING
# =============================================================================

cleanup() {
    info ""
    info "🛑 Shutting down TEP Integration system..."
    
    if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        info "Stopping backend (PID: $BACKEND_PID)..."
        kill "$BACKEND_PID" 2>/dev/null || true
        sleep 2
        # Force kill if still running
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            warning "Force killing backend process..."
            kill -9 "$BACKEND_PID" 2>/dev/null || true
        fi
    fi
    
    if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        info "Stopping frontend (PID: $FRONTEND_PID)..."
        kill "$FRONTEND_PID" 2>/dev/null || true
        sleep 2
        # Force kill if still running
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            warning "Force killing frontend process..."
            kill -9 "$FRONTEND_PID" 2>/dev/null || true
        fi
    fi
    
    success "System shutdown complete"
    exit 0
}

# Set up signal handlers for graceful shutdown
trap cleanup SIGINT SIGTERM EXIT

# =============================================================================
# DEPENDENCY CHECKING
# =============================================================================

check_dependencies() {
    info "Checking system dependencies..."
    
    local missing_deps=()
    
    # Check required commands
    local required_commands=("python" "npm" "curl")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error "Missing required dependencies: ${missing_deps[*]}"
        error "Please install the missing dependencies and try again"
        return 1
    fi
    
    success "All system dependencies found"
    return 0
}

# =============================================================================
# PORT CHECKING
# =============================================================================

check_port() {
    local port="$1"
    local service="$2"
    
    if lsof -Pi ":$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        warning "Port $port is already in use (required for $service)"
        warning "Please stop the service using port $port or choose a different port"
        return 1
    fi
    
    return 0
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    info "🏭 TEP Integration - Improved System Startup"
    info "============================================"
    info "Script: $0"
    info "Working directory: $(pwd)"
    info "Log file: $LOG_FILE"
    info ""
    
    # Check if we're in the right directory
    if [[ ! -f "src/backend/services/llm-analysis/app.py" ]] || [[ ! -f "src/frontend/package.json" ]]; then
        error "Please run this script from the integration folder"
        error "Expected files not found:"
        error "  - src/backend/services/llm-analysis/app.py"
        error "  - src/frontend/package.json"
        exit 1
    fi
    
    # Check system dependencies
    check_dependencies || exit 1
    
    # Check ports
    check_port "$BACKEND_PORT" "backend" || exit 1
    check_port "$FRONTEND_PORT" "frontend" || exit 1
    
    # Activate virtual environment
    activate_virtual_environment || exit 1
    
    info ""
    info "🚀 Starting TEP Integration services..."
    info ""
    
    # Start backend
    info "Starting backend server..."
    cd src/backend/services/llm-analysis
    python app.py &
    BACKEND_PID=$!
    cd ../../../..
    
    # Wait for backend to start
    info "⏳ Waiting for backend to initialize..."
    local backend_ready=false
    for i in {1..30}; do
        if curl -s "http://localhost:$BACKEND_PORT/status" > /dev/null 2>&1; then
            backend_ready=true
            break
        fi
        sleep 1
        info "Attempt $i/30: Waiting for backend..."
    done
    
    if [[ "$backend_ready" != true ]]; then
        error "Backend failed to start within 30 seconds"
        exit 1
    fi
    
    success "Backend running on http://localhost:$BACKEND_PORT"
    
    # Start frontend
    info "Starting frontend server..."
    cd src/frontend
    
    # Install dependencies if needed
    if [[ ! -d "node_modules" ]]; then
        info "📦 Installing frontend dependencies..."
        npm install
    fi
    
    npm run dev &
    FRONTEND_PID=$!
    cd ../..
    
    # Wait for frontend to start
    info "⏳ Waiting for frontend to initialize..."
    sleep 10
    
    success ""
    success "🎉 TEP Integration System is running!"
    success ""
    success "🌐 Access Points:"
    success "   • Frontend Dashboard: http://localhost:$FRONTEND_PORT"
    success "   • Backend API: http://localhost:$BACKEND_PORT"
    success "   • API Documentation: http://localhost:$BACKEND_PORT/docs"
    success ""
    success "🎛️ Features Available:"
    success "   • Real-time TEP monitoring with 33 operational ranges"
    success "   • Claude LLM integration for fault analysis"
    success "   • PCA-based anomaly detection"
    success "   • Enhanced charts with smart Y-axis scaling"
    success ""
    success "📊 Process Information:"
    success "   • Backend PID: $BACKEND_PID"
    success "   • Frontend PID: $FRONTEND_PID"
    success "   • Log file: $LOG_FILE"
    success ""
    success "Press Ctrl+C to stop both services"
    success ""
    
    # Wait for user to stop the system
    wait
}

# Run main function
main "$@"
