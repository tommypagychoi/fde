from pydantic import BaseModel, Field


class ExecuteRequest(BaseModel):
    clusterId: str = Field(default="prod-ha-cluster-01")
    namespace: str | None = Field(default=None)
    command: str = Field(..., examples=["kubectl get nodes"])
    requester: str = Field(default="dashboard")
    approvalNo: str | None = Field(default=None)


class ExecuteResponse(BaseModel):
    status: str
    allowed: bool
    stdout: str = ""
    stderr: str = ""
    auditId: str


class ItemsResponse(BaseModel):
    items: list[str]
