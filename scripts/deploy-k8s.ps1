param(
    [string]$Namespace = "fde-system",
    [string]$KeyPath = "$PSScriptRoot\..\secrets\fde_deploy_key",
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

& $SshExe -i $SshKey -p $RemotePort "${RemoteUser}@${RemoteHost}" "mkdir -p ${remoteDir}/deploy/k8s"
& $ScpExe -i $SshKey -P $RemotePort "$root\deploy\k8s\backend.yaml" "${RemoteUser}@${RemoteHost}:${remoteDir}/deploy/k8s/backend.yaml"
& $ScpExe -i $SshKey -P $RemotePort "$root\deploy\k8s\frontend.yaml" "${RemoteUser}@${RemoteHost}:${remoteDir}/deploy/k8s/frontend.yaml"

& $SshExe -i $SshKey -p $RemotePort "${RemoteUser}@${RemoteHost}" "kubectl create namespace ${Namespace} --dry-run=client -o yaml | kubectl apply -f -"

if (Test-Path $KeyPath) {
    & $ScpExe -i $SshKey -P $RemotePort $KeyPath "${RemoteUser}@${RemoteHost}:${remoteDir}/bastion.pem"
    & $SshExe -i $SshKey -p $RemotePort "${RemoteUser}@${RemoteHost}" "kubectl -n ${Namespace} create secret generic fde-bastion-key --from-file=bastion.pem=${remoteDir}/bastion.pem --dry-run=client -o yaml | kubectl apply -f - && rm -f ${remoteDir}/bastion.pem"
}
else {
    Write-Warning "Bastion key not found: $KeyPath. Create secret fde-bastion-key before backend starts."
}

& $SshExe -i $SshKey -p $RemotePort "${RemoteUser}@${RemoteHost}" "kubectl apply -f ${remoteDir}/deploy/k8s/backend.yaml && kubectl apply -f ${remoteDir}/deploy/k8s/frontend.yaml && kubectl -n ${Namespace} rollout status deployment/fde-backend && kubectl -n ${Namespace} rollout status deployment/fde-frontend"
