from datetime import datetime, timezone

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .audit import create_audit_id, save_audit_log
from .config import settings
from .runner import run_command
from .schemas import ExecuteRequest, ExecuteResponse, ItemsResponse
from .security import build_safe_command, validate_command


app = FastAPI(title=settings.APP_NAME)

origins = ["*"] if settings.CORS_ORIGINS == "*" else [v.strip() for v in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_token(x_api_token: str = Header(default="")) -> None:
    if x_api_token != settings.API_TOKEN:
        raise HTTPException(status_code=401, detail="invalid api token")


def kubectl_lines(command: str) -> list[str]:
    safe_command = build_safe_command(command, None, settings.KUBECONFIG_PATH)
    result = run_command(safe_command)
    if result.exit_code != 0:
        raise HTTPException(status_code=502, detail=result.stderr or "kubectl command failed")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/api/namespaces", response_model=ItemsResponse)
def namespaces(x_api_token: str = Header(default="")) -> ItemsResponse:
    require_token(x_api_token)
    items = kubectl_lines("kubectl get namespaces -o jsonpath='{.items[*].metadata.name}'")
    return ItemsResponse(items=items[0].split() if items else [])


@app.get("/api/deployments", response_model=ItemsResponse)
def deployments(namespace: str = Query(...), x_api_token: str = Header(default="")) -> ItemsResponse:
    require_token(x_api_token)
    command = f"kubectl get deployments -n {namespace} -o jsonpath='{{.items[*].metadata.name}}'"
    items = kubectl_lines(command)
    return ItemsResponse(items=items[0].split() if items else [])


@app.get("/api/pods", response_model=ItemsResponse)
def pods(namespace: str = Query(...), x_api_token: str = Header(default="")) -> ItemsResponse:
    require_token(x_api_token)
    command = f"kubectl get pods -n {namespace} -o jsonpath='{{.items[*].metadata.name}}'"
    items = kubectl_lines(command)
    return ItemsResponse(items=items[0].split() if items else [])


@app.post("/api/k8s/execute", response_model=ExecuteResponse)
def execute_kubectl(req: ExecuteRequest, x_api_token: str = Header(default="")) -> ExecuteResponse:
    require_token(x_api_token)
    audit_id = create_audit_id()
    allowed, reason = validate_command(req.command)

    save_audit_log(
        {
            "auditId": audit_id,
            "phase": "REQUESTED",
            "clusterId": req.clusterId,
            "namespace": req.namespace,
            "requester": req.requester,
            "approvalNo": req.approvalNo,
            "command": req.command,
            "allowed": allowed,
            "reason": reason,
        }
    )

    if not allowed:
        save_audit_log({"auditId": audit_id, "phase": "BLOCKED", "reason": reason})
        return ExecuteResponse(status="blocked", allowed=False, stderr=reason, auditId=audit_id)

    safe_command = build_safe_command(req.command, req.namespace, settings.KUBECONFIG_PATH)
    try:
        result = run_command(safe_command)
        status = "success" if result.exit_code == 0 else "failed"
        save_audit_log(
            {
                "auditId": audit_id,
                "phase": "COMPLETED",
                "status": status,
                "exitCode": result.exit_code,
                "stdoutPreview": result.stdout[:1000],
                "stderrPreview": result.stderr[:1000],
            }
        )
        return ExecuteResponse(status=status, allowed=True, stdout=result.stdout, stderr=result.stderr, auditId=audit_id)
    except Exception as exc:
        save_audit_log({"auditId": audit_id, "phase": "ERROR", "error": str(exc)})
        return ExecuteResponse(status="error", allowed=True, stderr=str(exc), auditId=audit_id)
