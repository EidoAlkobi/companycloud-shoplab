#!/usr/bin/env bash
set -euo pipefail
LOCAL_PORT="${FRONTEND_LOCAL_PORT:-8080}"
pkill -f "kubectl port-forward svc/frontend" 2>/dev/null || true
kubectl port-forward svc/frontend "${LOCAL_PORT}:8080" --address 0.0.0.0
