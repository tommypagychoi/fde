# FDE Enterprise Automation Console

This repository contains the GitHub-ready source for the FDE Kubernetes automation dashboard.

## Target Servers

- Kubernetes master/API target: `192.168.0.85` via `ccymproxmox.iptime.org:2085`, deploy user `root`
- Web server/Nginx target: `192.168.0.86` via `ccymproxmox.iptime.org:2086`, deploy user `root`
- Dashboard frontend: static HTML served by Nginx
- Backend API: FastAPI, executes approved `kubectl`/`helm` commands through SSH bastion or local mode

## Repository Layout

- `frontend/`: final dashboard HTML and Nginx container config
- `backend/`: FastAPI source, Dockerfile, runtime configuration
- `deploy/k8s/`: Kubernetes manifests for backend/frontend
- `deploy/monitoring/`: kube-prometheus-stack Helm values
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

1. The manifests use `ghcr.io/tommypagychoi/fde/backend:latest` and `ghcr.io/tommypagychoi/fde/frontend:latest`.
2. Put the SSH private key at `secrets/fde_deploy_key`.
3. Run:

```powershell
.\scripts\deploy-k8s.ps1
```

Remote SSH default:

```text
ccymproxmox.iptime.org:2085 / root
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
.\scripts\deploy-webserver.ps1
```

Then open:

```text
http://192.168.0.86
```

The web server proxies `/api/*` to `http://192.168.0.85:30080/api/*`. The backend SSH execution target uses root's kubeconfig at `/root/.kube/config`.

## Monitoring Deploy

Install Grafana and Prometheus with `kube-prometheus-stack`:

```powershell
.\scripts\install-monitoring.ps1
```

Monitoring URLs:

```text
Grafana:    http://192.168.0.86/grafana/
Prometheus: http://192.168.0.86/prometheus
Direct Grafana NodePort: http://192.168.0.81:32000
Direct Prometheus NodePort: http://192.168.0.85:32001
```

Default Grafana login:

```text
admin / fde-admin
```

## Dashboard Token

The frontend reads the API token from browser local storage first:

```javascript
localStorage.setItem('FDE_API_TOKEN', 'change-this-token')
```

Use the same value in `backend/.env` or the Kubernetes secret.
