#!/usr/bin/env bash
set -euo pipefail
kubectl delete -f k8s/ --ignore-not-found=true || true
kubectl delete job background-cpu-noise background-cpu-noise-limited --ignore-not-found=true || true
