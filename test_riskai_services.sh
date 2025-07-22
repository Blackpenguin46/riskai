#!/bin/bash

echo "Testing RiskAI Services..."
echo "-------------------------"

# Test frontend
echo "Testing Frontend (http://localhost:9001)..."
curl -s -o /dev/null -w "Frontend Status: %{http_code}\n" http://localhost:9001

# Test backend
echo "Testing Backend (http://localhost:9000/health)..."
curl -s -o /dev/null -w "Backend Status: %{http_code}\n" http://localhost:9000/health

# Get backend response
echo "Backend Response:"
curl -s http://localhost:9000/health

echo "-------------------------"
echo "If both services return status code 200, they are running correctly."
echo "If you still can't access them in your browser, try the following:"
echo "1. Try a different browser"
echo "2. Clear your browser cache"
echo "3. Check if any security software is blocking the connections"
echo "4. Try accessing with IP address instead of localhost: http://127.0.0.1:9001"