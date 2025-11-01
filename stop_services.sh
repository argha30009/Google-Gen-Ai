#!/bin/bash

# Stop all microservices
echo "🛑 Stopping all microservices..."

# Kill all python server processes
pkill -f "python.*server.py" 2>/dev/null

# Wait a moment
sleep 2

# Verify they're stopped
if pgrep -f "python.*server.py" > /dev/null; then
    echo "⚠️  Some processes are still running. Forcing kill..."
    pkill -9 -f "python.*server.py" 2>/dev/null
    sleep 1
fi

# Check ports
PORTS="8000 8001 8002 8003"
for port in $PORTS; do
    if netstat -ano | grep ":$port " | grep LISTENING > /dev/null 2>&1; then
        echo "⚠️  Port $port is still in use"
    else
        echo "✓ Port $port is free"
    fi
done

echo ""
echo "✅ All services stopped"
