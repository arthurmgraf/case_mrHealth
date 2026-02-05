#!/bin/bash
# Deploy Airflow, Superset, and Grafana to K3s
# Run this script from the server via SSH

set -e

echo "=== Deploying Airflow ==="

# Apply Airflow manifests
kubectl apply -f /tmp/k8s/airflow/configmap.yaml
kubectl apply -f /tmp/k8s/airflow/pvc-dags.yaml
kubectl apply -f /tmp/k8s/airflow/pvc-logs.yaml
kubectl apply -f /tmp/k8s/airflow/secret-gcp.yaml
kubectl apply -f /tmp/k8s/airflow/postgres.yaml
kubectl apply -f /tmp/k8s/airflow/webserver.yaml
kubectl apply -f /tmp/k8s/airflow/scheduler.yaml

echo "Waiting for Airflow Postgres to be ready..."
kubectl wait --for=condition=ready pod -l app=airflow-postgres -n mrhealth-db --timeout=120s

echo "=== Deploying Superset ==="

# Apply Superset manifests
kubectl apply -f /tmp/k8s/superset/configmap.yaml
kubectl apply -f /tmp/k8s/superset/deployment.yaml

echo "=== Deploying Grafana ==="

# Create Grafana namespace
kubectl apply -f /tmp/k8s/grafana/namespace.yaml

echo "Waiting for namespace mrhealth-monitoring..."
kubectl wait --for=jsonpath='{.status.phase}'=Active namespace/mrhealth-monitoring --timeout=30s

# Create dashboard ConfigMap from JSON files
kubectl create configmap grafana-dashboards-files \
  --from-file=/tmp/k8s/grafana/dashboards/ \
  -n mrhealth-monitoring \
  --dry-run=client -o yaml | kubectl apply -f -

# Apply Grafana manifests
kubectl apply -f /tmp/k8s/grafana/pvc.yaml
kubectl apply -f /tmp/k8s/grafana/secret.yaml
kubectl apply -f /tmp/k8s/grafana/configmap.yaml
kubectl apply -f /tmp/k8s/grafana/deployment.yaml
kubectl apply -f /tmp/k8s/grafana/service.yaml

echo "Waiting for Grafana to be ready..."
kubectl wait --for=condition=ready pod -l app=grafana -n mrhealth-monitoring --timeout=120s

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Access URLs:"
echo "  Airflow:  http://<YOUR-K3S-IP>:30180  (check credentials in Secret Manager)"
echo "  Superset: http://<YOUR-K3S-IP>:30088  (check credentials in Secret Manager)"
echo "  Grafana:  http://<YOUR-K3S-IP>:30300  (default: admin/admin -- change immediately)"
echo ""
echo "Check pod status with:"
echo "  kubectl get pods -n mrhealth-db"
echo "  kubectl get pods -n mrhealth-monitoring"
echo ""
echo "IMPORTANT: Before using Grafana with BigQuery, replace the placeholder"
echo "  GCP service account key in the grafana-gcp-credentials secret:"
echo "    kubectl create secret generic grafana-gcp-credentials \\"
echo "      --from-file=service-account.json=<path-to-key.json> \\"
echo "      -n mrhealth-monitoring --dry-run=client -o yaml | kubectl apply -f -"
