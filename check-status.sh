#!/bin/bash

echo "=== Docker Container Status ==="
docker compose ps

echo ""
echo "=== Docker Compose Logs (Last 20 lines) ==="
docker compose logs --tail=20 2>/dev/null || echo "No logs yet - containers may not be running"

echo ""
echo "=== Checking Services ==="
echo "Testing backend (http://localhost:8000)..."
curl -s http://localhost:8000/health 2>/dev/null && echo "✓ Backend is responding" || echo "✗ Backend not responding"

echo ""
echo "Testing frontend (http://localhost:3000)..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null | grep -q "200" && echo "✓ Frontend is responding" || echo "✗ Frontend not responding"

echo ""
echo "=== Quick Commands ==="
echo "Start services: docker compose up -d"
echo "View logs: docker compose logs -f"
echo "Stop services: docker compose down"
echo "Restart: docker compose restart"
