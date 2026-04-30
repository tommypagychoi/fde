# FDE Enterprise Automation Console

GitHub-ready source for the FDE Kubernetes automation dashboard.

## Target Servers

- Kubernetes master/API target: `192.168.0.85` via `ccymproxmox.iptime.org:2085`, user `tommypagy`
- Web server/Nginx target: `192.168.0.86` via `ccymproxmox.iptime.org:2086`, user `tommypagy`
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

## Kubernetes Deploy

The script defaults to `ccymproxmox.iptime.org:2085` and `secrets/fde_deploy_key`.

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

The script defaults to `ccymproxmox.iptime.org:2086` and `secrets/fde_deploy_key`.

```powershell
.\scripts\deploy-webserver.ps1
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
