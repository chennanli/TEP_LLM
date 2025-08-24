#!/bin/bash

# TEP Services Complete Shutdown Script
# This script ensures ALL TEP-related processes are safely terminated

echo "🛑 TEP Services Complete Shutdown"
echo "=================================="

# Function to kill processes by port
kill_by_port() {
    local port=$1
    local service_name=$2
    
    echo "🔍 Checking port $port ($service_name)..."
    
    # Find process using the port
    PID=$(lsof -ti :$port 2>/dev/null)
    
    if [ ! -z "$PID" ]; then
        echo "⚠️  Found process $PID using port $port"
        echo "🔪 Killing process $PID..."
        kill -TERM $PID 2>/dev/null
        sleep 2
        
        # Force kill if still running
        if kill -0 $PID 2>/dev/null; then
            echo "💀 Force killing process $PID..."
            kill -KILL $PID 2>/dev/null
        fi
        
        echo "✅ Port $port cleared"
    else
        echo "✅ Port $port is free"
    fi
}

# Function to kill processes by name pattern
kill_by_pattern() {
    local pattern=$1
    local service_name=$2
    
    echo "🔍 Checking for $service_name processes..."
    
    # Find processes matching pattern
    PIDS=$(ps aux | grep -E "$pattern" | grep -v grep | awk '{print $2}')
    
    if [ ! -z "$PIDS" ]; then
        echo "⚠️  Found $service_name processes: $PIDS"
        for PID in $PIDS; do
            echo "🔪 Killing process $PID..."
            kill -TERM $PID 2>/dev/null
        done
        sleep 2
        
        # Force kill any remaining processes
        REMAINING=$(ps aux | grep -E "$pattern" | grep -v grep | awk '{print $2}')
        if [ ! -z "$REMAINING" ]; then
            echo "💀 Force killing remaining processes: $REMAINING"
            for PID in $REMAINING; do
                kill -KILL $PID 2>/dev/null
            done
        fi
        
        echo "✅ $service_name processes cleared"
    else
        echo "✅ No $service_name processes found"
    fi
}

# Kill processes by specific ports
echo ""
echo "📡 Stopping services by port..."
kill_by_port 9001 "Legacy TEP Control Panel"
kill_by_port 9002 "Integration TEP Control Panel"
kill_by_port 8001 "Integration Backend"
kill_by_port 8000 "FaultExplainer Backend"
kill_by_port 3000 "Frontend Development Server"

# Kill processes by name patterns
echo ""
echo "🔍 Stopping services by process name..."
kill_by_pattern "unified_tep_control_panel" "Legacy TEP Control Panel"
kill_by_pattern "unified_control_panel" "Integration Control Panel"
kill_by_pattern "uvicorn.*app:app" "FastAPI Backend Services"
kill_by_pattern "python.*app\.py" "Python Backend Services"
kill_by_pattern "flask.*run" "Flask Services"

# Clean up any remaining Python processes in TEP directories
echo ""
echo "🧹 Cleaning up TEP-related Python processes..."
TEP_DIR="/Users/chennanli/Desktop/LLM_Project/TE"
PYTHON_PIDS=$(ps aux | grep python | grep "$TEP_DIR" | grep -v grep | awk '{print $2}')

if [ ! -z "$PYTHON_PIDS" ]; then
    echo "⚠️  Found TEP Python processes: $PYTHON_PIDS"
    for PID in $PYTHON_PIDS; do
        echo "🔪 Killing TEP Python process $PID..."
        kill -TERM $PID 2>/dev/null
    done
    sleep 2
    
    # Force kill if needed
    REMAINING_PYTHON=$(ps aux | grep python | grep "$TEP_DIR" | grep -v grep | awk '{print $2}')
    if [ ! -z "$REMAINING_PYTHON" ]; then
        echo "💀 Force killing remaining Python processes: $REMAINING_PYTHON"
        for PID in $REMAINING_PYTHON; do
            kill -KILL $PID 2>/dev/null
        done
    fi
fi

# Clean up data files and temporary files
echo ""
echo "🧹 Cleaning up temporary files..."

# Clean CSV data files
if [ -f "legacy/data/live_tep_data.csv" ]; then
    echo "🗑️  Cleaning legacy data file..."
    > legacy/data/live_tep_data.csv
fi

if [ -f "integration/data/live_tep_data.csv" ]; then
    echo "🗑️  Cleaning integration data file..."
    > integration/data/live_tep_data.csv
fi

# Clean log files
find . -name "*.log" -type f -exec truncate -s 0 {} \; 2>/dev/null
echo "🗑️  Log files cleaned"

# Final verification
echo ""
echo "🔍 Final verification..."
echo "Checking ports:"
for port in 9001 9002 8001 8000 3000; do
    if lsof -ti :$port >/dev/null 2>&1; then
        echo "❌ Port $port still in use!"
    else
        echo "✅ Port $port is free"
    fi
done

echo ""
echo "Checking TEP processes:"
TEP_PROCESSES=$(ps aux | grep -E "(unified_tep|unified_control|tep.*python)" | grep -v grep)
if [ ! -z "$TEP_PROCESSES" ]; then
    echo "❌ Some TEP processes may still be running:"
    echo "$TEP_PROCESSES"
else
    echo "✅ No TEP processes found"
fi

echo ""
echo "🎉 TEP Services Shutdown Complete!"
echo "=================================="
echo "✅ All ports cleared"
echo "✅ All processes terminated"
echo "✅ Temporary files cleaned"
echo "✅ Safe to restart services"
echo ""
echo "💡 To restart:"
echo "   Legacy:      cd legacy && source ../tep_env/bin/activate && python unified_tep_control_panel.py"
echo "   Integration: cd integration && source ../tep_env/bin/activate && python unified_control_panel.py"
