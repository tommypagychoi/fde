# FDE Enterprise Automation Console

GitHub-ready source for the FDE Kubernetes automation dashboard.

Repository upload commit: `a4bf3bde43e4029e7f6f76d4523e662ab8c908ff`

## Target Servers

- Kubernetes master/API target: `192.168.0.85`
- Web server/Nginx target: `192.168.0.86`
- Dashboard frontend: static HTML served by Nginx
- Backend API: FastAPI, executes approved `kubectl`/`helm` commands through SSH bastion or local mode

## Repository Layout

- `frontend/`: dashboard HTML and Nginx container config
- `backend/`: FastAPI source, Dockerfile, runtime configuration
- `deploy/k8s/`: Kubernetes manifests for backend/frontend
- `deploy/nginx-webserver.conf`: Nginx config for `192.168.0.86`
- `scripts/`: local bootstrap and deployment helpers
- `.github/workflows/`: GHCR Docker image build workflow

## Local Run

```powershell
Copy-Item backend\.env.example backend\.env
notepad backend\.env
docker compose up --build
```

Open:

```text
http://127.0.0.1:8080
http://127.0.0.1:8000/health
```

If you do not use Docker:

```powershell
.\scripts\bootstrap-local.ps1
```

## Kubernetes Deploy

1. Replace `ghcr.io/tommypagychoi/fde/...` in `deploy/k8s/*.yaml` if you fork or rename the repo.
2. Put the SSH private key at `secrets/bastion.pem`.
3. Run:

```powershell
.\scripts\deploy-k8s.ps1 -KeyPath .\secrets\bastion.pem
```

Backend NodePort:

```text
http://192.168.0.85:30080/health
```

Frontend NodePort:

```text
http://192.168.0.85:30081
```

## Web Server Deploy

Deploy the static dashboard and Nginx reverse proxy to `192.168.0.86`:

```powershell
.\scripts\deploy-webserver.ps1 -WebServer 192.168.0.86 -User ubuntu -SshKey C:\Users\lg202\.ssh\id_rsa
```

Then open:

```text
http://192.168.0.86
```

The web server proxies `/api/*` to `http://192.168.0.85:30080/api/*`.

## Dashboard Token

The frontend reads the API token from browser local storage first:

```javascript
localStorage.setItem('FDE_API_TOKEN', 'change-this-token')
```

Use the same value in `backend/.env` or the Kubernetes secret.
