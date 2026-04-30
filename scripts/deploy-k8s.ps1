param(
    [string]$Namespace = "fde-system",
    [string]$KeyPath = ".\secrets\bastion.pem"
)

$ErrorActionPreference = "Stop"

kubectl create namespace $Namespace --dry-run=client -o yaml | kubectl apply -f -

if (Test-Path $KeyPath) {
    kubectl -n $Namespace create secret generic fde-bastion-key `
        --from-file=bastion.pem=$KeyPath `
        --dry-run=client -o yaml | kubectl apply -f -
}
else {
    Write-Warning "Bastion key not found: $KeyPath. Create secret fde-bastion-key before backend starts."
}

kubectl apply -f "$PSScriptRoot\..\deploy\k8s\backend.yaml"
kubectl apply -f "$PSScriptRoot\..\deploy\k8s\frontend.yaml"
kubectl -n $Namespace rollout status deployment/fde-backend
kubectl -n $Namespace rollout status deployment/fde-frontend
