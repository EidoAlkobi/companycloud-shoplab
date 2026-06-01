#!/usr/bin/env bash
set -euo pipefail
kubectl rollout restart deployment/frontend
kubectl rollout status deployment/frontend --timeout=120s
