param(
    [string]$RemoteHost = "ccymproxmox.iptime.org",
    [string]$RemoteUser = "root",
    [int]$RemotePort = 2085,
    [string]$SshKey = "$PSScriptRoot\..\secrets\fde_deploy_key",
    [string]$SshExe = "C:\Windows\System32\OpenSSH\ssh.exe",
    [string]$ScpExe = "C:\Windows\System32\OpenSSH\scp.exe"
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path "$PSScriptRoot\.."
$remoteDir = "/tmp/fde-deploy"

& $SshExe -i $SshKey -p $RemotePort "${RemoteUser}@${RemoteHost}" "mkdir -p ${remoteDir}/deploy/monitoring"
& $ScpExe -i $SshKey -P $RemotePort "$root\deploy\monitoring\kube-prometheus-stack-values.yaml" "${RemoteUser}@${RemoteHost}:${remoteDir}/deploy/monitoring/kube-prometheus-stack-values.yaml"

& $SshExe -i $SshKey -p $RemotePort "${RemoteUser}@${RemoteHost}" @"
set -e
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
helm upgrade --install fde-monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values ${remoteDir}/deploy/monitoring/kube-prometheus-stack-values.yaml \
  --wait \
  --timeout 10m
kubectl -n monitoring rollout status deployment/fde-monitoring-grafana --timeout=300s
kubectl -n monitoring get pods,svc -o wide
"@
