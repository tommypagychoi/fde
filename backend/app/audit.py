import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import settings


def create_audit_id() -> str:
    return "AUDIT-" + uuid.uuid4().hex[:12].upper()


def save_audit_log(payload: dict[str, Any]) -> None:
    entry = {**payload, "loggedAt": datetime.now(timezone.utc).isoformat()}
    path = Path(settings.AUDIT_LOG_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
