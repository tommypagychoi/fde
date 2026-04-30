param(
    [string]$RemoteHost = "ccymproxmox.iptime.org",
    [string]$User = "root",
    [int]$RemotePort = 2086,
    [string]$SshKey = "$PSScriptRoot\..\secrets\fde_deploy_key",
    [string]$SshExe = "C:\Windows\System32\OpenSSH\ssh.exe",
    [string]$ScpExe = "C:\Windows\System32\OpenSSH\scp.exe"
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path "$PSScriptRoot\.."

& $ScpExe -i $SshKey -P $RemotePort "$root\frontend\index.html" "${User}@${RemoteHost}:/tmp/index.html"
& $ScpExe -i $SshKey -P $RemotePort "$root\deploy\nginx-webserver.conf" "${User}@${RemoteHost}:/tmp/fde.conf"
& $SshExe -i $SshKey -p $RemotePort "${User}@${RemoteHost}" "mkdir -p /var/www/fde && mv /tmp/index.html /var/www/fde/index.html && mv /tmp/fde.conf /etc/nginx/sites-available/fde.conf && ln -sf /etc/nginx/sites-available/fde.conf /etc/nginx/sites-enabled/fde.conf && nginx -t && systemctl reload nginx"
