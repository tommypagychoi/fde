import shlex


ALLOWED_PREFIXES = [
    "kubectl get nodes",
    "kubectl get pods",
    "kubectl get pods -A",
    "kubectl get pod",
    "kubectl get svc",
    "kubectl get services",
    "kubectl get namespaces",
    "kubectl get namespace",
    "kubectl get deployments",
    "kubectl get deployment",
    "kubectl get pvc",
    "kubectl describe node",
    "kubectl describe pod",
    "kubectl top node",
    "kubectl top pod",
    "kubectl logs",
    "kubectl rollout restart deployment",
    "kubectl delete pod",
    "kubectl delete pods --all",
    "helm list",
]

BLOCKED_TOKENS = [
    ";",
    "&&",
    "||",
    "|",
    "`",
    "$(",
    ">",
    "<",
    "--token",
    "--kubeconfig",
    "config",
    "proxy",
    "port-forward",
    "cp",
    "edit",
    "patch",
    "apply",
    "create",
    "replace",
    "drain",
    "cordon",
    "uncordon",
    "scale",
    "exec",
]


def normalize_command(command: str) -> str:
    return " ".join(command.strip().split())


def validate_command(command: str) -> tuple[bool, str]:
    cmd = normalize_command(command)
    if not cmd:
        return False, "empty command"

    try:
        parts = shlex.split(cmd)
    except ValueError:
        return False, "invalid shell syntax"

    if not parts or parts[0] not in {"kubectl", "helm"}:
        return False, "kubectl or helm command only"

    lowered_parts = [p.lower() for p in parts]
    lowered_cmd = " ".join(lowered_parts)

    for token in BLOCKED_TOKENS:
        if token in lowered_parts or token in lowered_cmd:
            return False, f"blocked token detected: {token}"

    if not any(lowered_cmd == p or lowered_cmd.startswith(p + " ") for p in ALLOWED_PREFIXES):
        return False, "command is not in whitelist"

    return True, "allowed"


def build_safe_command(command: str, namespace: str | None, kubeconfig_path: str) -> str:
    cmd = normalize_command(command)
    parts = shlex.split(cmd)

    if namespace and parts[0] == "kubectl" and "-A" not in parts and "--all-namespaces" not in parts:
        has_namespace = "-n" in parts or "--namespace" in parts
        namespaced_verbs = {"get", "describe", "logs", "top", "rollout", "delete"}
        if len(parts) > 1 and parts[1] in namespaced_verbs and not has_namespace:
            parts.extend(["-n", namespace])

    if parts[0] == "kubectl":
        parts.extend(["--kubeconfig", kubeconfig_path])

    return " ".join(shlex.quote(p) for p in parts)
