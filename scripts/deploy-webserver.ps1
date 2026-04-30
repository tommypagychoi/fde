param(
    [string]$WebServer = "192.168.0.86",
    [string]$User = "ubuntu",
    [string]$SshKey = "$env:USERPROFILE\.ssh\id_rsa"
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path "$PSScriptRoot\.."

scp -i $SshKey "$root\frontend\index.html" "${User}@${WebServer}:/tmp/index.html"
scp -i $SshKey "$root\deploy\nginx-webserver.conf" "${User}@${WebServer}:/tmp/fde.conf"
ssh -i $SshKey "${User}@${WebServer}" "sudo mkdir -p /var/www/fde && sudo mv /tmp/index.html /var/www/fde/index.html && sudo mv /tmp/fde.conf /etc/nginx/sites-available/fde.conf && sudo ln -sf /etc/nginx/sites-available/fde.conf /etc/nginx/sites-enabled/fde.conf && sudo nginx -t && sudo systemctl reload nginx"
