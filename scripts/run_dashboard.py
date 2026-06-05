from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
URL = "http://127.0.0.1:8001"


def main() -> None:
    stdout = (ROOT / "uhms_server_stdout.log").open("ab")
    stderr = (ROOT / "uhms_server_stderr.log").open("ab")
    subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=ROOT,
        stdout=stdout,
        stderr=stderr,
        creationflags=0x08000000 if sys.platform == "win32" else 0,
    )
    time.sleep(4)
    with urllib.request.urlopen(URL, timeout=10) as response:
        body = response.read()
    print(f"{URL} status={response.status} bytes={len(body)}")


if __name__ == "__main__":
    main()

