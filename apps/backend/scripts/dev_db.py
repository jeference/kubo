"""Postgres local sem Docker: usa os binários do pacote `pgserver`, na porta 5433.

Cria o cluster em `_pgdata/` na primeira execução e o banco `kubo`.
Fica em primeiro plano até Ctrl+C (`--detach` só inicia e sai). Apenas para desenvolvimento.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

import pgserver
import tzdata

BIN = Path(pgserver.__file__).parent / "pginstall" / "bin"
DATA = Path(__file__).resolve().parent.parent / "_pgdata"
PORT = "5433"


def run(name: str, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run([str(BIN / name), *args], check=check, text=True, capture_output=True)


def ensure_timezone_data() -> None:
    """O pacote `pgserver` no Windows vem sem fusos horários, e o Django exige "UTC"."""
    target = BIN.parent / "share" / "postgresql" / "timezone"
    if not target.exists():
        shutil.copytree(Path(tzdata.__file__).parent / "zoneinfo", target)


def main() -> int:
    ensure_timezone_data()
    if not (DATA / "PG_VERSION").exists():
        run(
            "initdb",
            "-D",
            str(DATA),
            "-U",
            "kubo",
            "--auth=trust",
            "--encoding=UTF8",
            "--locale=C",
        )
    status = run("pg_ctl", "-D", str(DATA), "status", check=False)
    if status.returncode != 0:
        subprocess.run(
            [
                str(BIN / "pg_ctl"),
                "-D",
                str(DATA),
                "-w",
                "-o",
                f"-p {PORT}",
                "-l",
                str(DATA / "server.log"),
                "start",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
    run("createdb", "-h", "127.0.0.1", "-p", PORT, "-U", "kubo", "kubo", check=False)
    print(f"Postgres pronto em 127.0.0.1:{PORT}.", flush=True)
    if "--detach" in sys.argv:
        return 0
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        subprocess.run([str(BIN / "pg_ctl"), "-D", str(DATA), "-m", "fast", "stop"], check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
