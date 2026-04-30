from dataclasses import dataclass
import subprocess

import paramiko

from .config import settings


@dataclass
class CommandResult:
    stdout: str
    stderr: str
    exit_code: int


def run_command(command: str) -> CommandResult:
    if settings.EXECUTION_MODE.lower() == "local":
        return _run_local(command)
    return _run_ssh(command)


def _run_local(command: str) -> CommandResult:
    completed = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=settings.COMMAND_TIMEOUT,
        check=False,
    )
    return CommandResult(completed.stdout, completed.stderr, completed.returncode)


def _run_ssh(command: str) -> CommandResult:
    key = paramiko.RSAKey.from_private_key_file(settings.BASTION_KEY_PATH)
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=settings.BASTION_HOST,
            port=settings.BASTION_PORT,
            username=settings.BASTION_USER,
            pkey=key,
            timeout=settings.SSH_TIMEOUT,
            banner_timeout=settings.SSH_TIMEOUT,
            auth_timeout=settings.SSH_TIMEOUT,
        )
        _, stdout, stderr = client.exec_command(command, timeout=settings.COMMAND_TIMEOUT, get_pty=False)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        code = stdout.channel.recv_exit_status()
        return CommandResult(out, err, code)
    finally:
        client.close()
