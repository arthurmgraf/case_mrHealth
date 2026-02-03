#!/bin/bash
# Deploy Airflow and Superset to mrhealth-db namespace
# Run this script from the server via SSH

set -e

echo "=== Deploying Airflow ==="

# Apply Airflow manifests
kubectl apply -f /tmp/k8s/airflow/configmap.yaml
kubectl apply -f /tmp/k8s/airflow/postgres.yaml
kubectl apply -f /tmp/k8s/airflow/webserver.yaml
kubectl apply -f /tmp/k8s/airflow/scheduler.yaml

echo "Waiting for Airflow Postgres to be ready..."
kubectl wait --for=condition=ready pod -l app=airflow-postgres -n mrhealth-db --timeout=120s

echo "=== Deploying Superset ==="

# Apply Superset manifests
kubectl apply -f /tmp/k8s/superset/configmap.yaml
kubectl apply -f /tmp/k8s/superset/deployment.yaml

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Access URLs:"
echo "  Airflow:  http://<YOUR-K3S-IP>:30080  (check credentials in Secret Manager)"
echo "  Superset: http://<YOUR-K3S-IP>:30088  (check credentials in Secret Manager)"
echo ""
echo "Check pod status with:"
echo "  kubectl get pods -n mrhealth-db"
