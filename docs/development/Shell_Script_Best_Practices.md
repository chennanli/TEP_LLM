# Shell Script Best Practices for TEP Integration System

## 🎯 **Overview**

This document outlines best practices for writing robust shell scripts for the TEP (Tennessee Eastman Process) integration system, with specific focus on virtual environment handling and cross-platform compatibility.

## 🔧 **Virtual Environment Best Practices**

### **❌ Common Mistakes**

```bash
# BAD: Hard-coded paths
source ../tep_env/bin/activate

# BAD: No error checking
source $VENV_PATH/bin/activate
python app.py

# BAD: Platform-specific assumptions
source venv/bin/activate  # Fails on Windows
```

### **✅ Recommended Approach**

```bash
# GOOD: Flexible virtual environment discovery
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

# GOOD: Cross-platform activation
get_activation_script() {
    local venv_path="$1"
    
    if [[ -f "$venv_path/bin/activate" ]]; then
        echo "$venv_path/bin/activate"      # Unix/Linux/macOS
    elif [[ -f "$venv_path/Scripts/activate" ]]; then
        echo "$venv_path/Scripts/activate"  # Windows
    else
        return 1
    fi
}

# GOOD: Verification after activation
activate_virtual_environment() {
    local activate_script
    if ! activate_script=$(get_activation_script "$venv_path"); then
        error "Activation script not found"
        return 1
    fi
    
    # Source the activation script
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
    fi
    
    return 0
}
```

## 📜 **Shell Script Structure Best Practices**

### **1. Strict Error Handling**

```bash
#!/bin/bash

# Exit on error, undefined variables, pipe failures
set -euo pipefail

# Secure Internal Field Separator
IFS=$'\n\t'
```

### **2. Constants and Configuration**

```bash
# Use readonly for constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
readonly VENV_NAME="${VENV_NAME:-tep_env}"  # Environment variable with default
readonly LOG_FILE="${SCRIPT_DIR}/startup.log"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color
```

### **3. Logging and User Feedback**

```bash
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
```

### **4. Process Management and Cleanup**

```bash
# Process tracking
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    info "🛑 Shutting down system..."
    
    # Graceful shutdown with fallback to force kill
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
    
    success "System shutdown complete"
    exit 0
}

# Set up signal handlers for graceful shutdown
trap cleanup SIGINT SIGTERM EXIT
```

### **5. Dependency Checking**

```bash
check_dependencies() {
    info "Checking system dependencies..."
    
    local missing_deps=()
    local required_commands=("python" "npm" "curl")
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error "Missing required dependencies: ${missing_deps[*]}"
        return 1
    fi
    
    success "All system dependencies found"
    return 0
}
```

### **6. Port Checking**

```bash
check_port() {
    local port="$1"
    local service="$2"
    
    if lsof -Pi ":$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        warning "Port $port is already in use (required for $service)"
        return 1
    fi
    
    return 0
}
```

## 🌐 **Cross-Platform Considerations**

### **File Paths**
```bash
# GOOD: Use forward slashes (work on all platforms)
readonly CONFIG_PATH="$SCRIPT_DIR/config/settings.json"

# GOOD: Use proper path joining
readonly FULL_PATH="$(cd "$SCRIPT_DIR" && pwd)/relative/path"
```

### **Command Availability**
```bash
# GOOD: Check command availability before use
if command -v lsof &> /dev/null; then
    # Use lsof for port checking
else
    # Fallback method for port checking
fi
```

### **Virtual Environment Activation**
```bash
# GOOD: Support both Unix and Windows paths
if [[ -f "$venv_path/bin/activate" ]]; then
    source "$venv_path/bin/activate"        # Unix/Linux/macOS
elif [[ -f "$venv_path/Scripts/activate" ]]; then
    source "$venv_path/Scripts/activate"    # Windows
fi
```

## 📋 **TEP Integration Specific Guidelines**

### **Virtual Environment Requirements**
- Always check for `tep_env` in multiple locations
- Verify Python version compatibility
- Ensure all required packages are installed
- Provide clear error messages for missing dependencies

### **Service Management**
- Start backend before frontend
- Wait for backend health check before proceeding
- Provide clear access URLs and port information
- Handle graceful shutdown of both services

### **Error Recovery**
- Provide specific error messages with solutions
- Create log files for debugging
- Offer fallback options when possible
- Clean up processes on script exit

## 🎯 **Example Usage**

```bash
# Using the improved startup script
cd integration
./start-system-improved.sh

# With custom virtual environment name
VENV_NAME=my_custom_env ./start-system-improved.sh

# With custom ports
BACKEND_PORT=8080 FRONTEND_PORT=3000 ./start-system-improved.sh
```

## 📚 **Additional Resources**

- **ShellCheck**: Use `shellcheck script.sh` to validate scripts
- **Bash Manual**: https://www.gnu.org/software/bash/manual/
- **POSIX Compliance**: For maximum portability
- **Testing**: Test scripts on different platforms and shells

## ✅ **Checklist for New Scripts**

- [ ] Use `set -euo pipefail` for strict error handling
- [ ] Define readonly constants at the top
- [ ] Implement proper logging functions
- [ ] Add signal handlers for cleanup
- [ ] Check dependencies before execution
- [ ] Support cross-platform virtual environment activation
- [ ] Provide clear user feedback and error messages
- [ ] Test on target platforms (macOS, Linux, Windows if applicable)
- [ ] Run through ShellCheck for validation
- [ ] Document usage and requirements
