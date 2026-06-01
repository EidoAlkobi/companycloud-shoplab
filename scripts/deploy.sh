#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Building image..."
docker build -t companycloud-shoplab:local .
echo "Importing image into k3s..."
docker save companycloud-shoplab:local -o /tmp/companycloud-shoplab.tar
sudo k3s ctr images import /tmp/companycloud-shoplab.tar
rm -f /tmp/companycloud-shoplab.tar
echo "Applying manifests..."
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/catalog.yaml
kubectl apply -f k8s/cart.yaml
kubectl apply -f k8s/payment.yaml
kubectl apply -f k8s/inventory.yaml
kubectl apply -f k8s/recommendation.yaml
kubectl apply -f k8s/checkout.yaml
kubectl apply -f k8s/worker.yaml
kubectl wait --for=condition=available deployment/frontend --timeout=180s
kubectl get pods
kubectl get svc
