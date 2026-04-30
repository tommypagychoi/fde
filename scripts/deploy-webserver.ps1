param(
    [string]$RemoteHost = "ccymproxmox.iptime.org",
    [string]$User = "tommypagy",
    [int]$RemotePort = 2086,
    [string]$SshKey = "$PSScriptRoot\..\secrets\fde_deploy_key"
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path "$PSScriptRoot\.."

scp -i $SshKey -P $RemotePort "$root\frontend\index.html" "${User}@${RemoteHost}:/tmp/index.html"
scp -i $SshKey -P $RemotePort "$root\deploy\nginx-webserver.conf" "${User}@${RemoteHost}:/tmp/fde.conf"
ssh -i $SshKey -p $RemotePort "${User}@${RemoteHost}" "sudo mkdir -p /var/www/fde && sudo mv /tmp/index.html /var/www/fde/index.html && sudo mv /tmp/fde.conf /etc/nginx/sites-available/fde.conf && sudo ln -sf /etc/nginx/sites-available/fde.conf /etc/nginx/sites-enabled/fde.conf && sudo nginx -t && sudo systemctl reload nginx"
