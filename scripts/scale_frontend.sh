#!/usr/bin/env bash
set -euo pipefail
REPLICAS="${1:-1}"
kubectl scale deployment frontend --replicas="$REPLICAS"
kubectl rollout status deployment/frontend --timeout=120s
kubectl get deploy frontend
