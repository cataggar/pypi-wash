"""wash CLI - a tool for wasmCloud development."""

import os
import subprocess
import sys
from pathlib import Path

try:
    from importlib.metadata import version

    __version__ = version("wash-bin")
except Exception:
    __version__ = "0.0.0"

_BIN = "wash.exe" if sys.platform == "win32" else "wash"


def _binary_path() -> Path:
    """Return the path to the wash binary."""
    return Path(__file__).parent / _BIN


def main() -> None:
    """Entry point that delegates to the native binary."""
    binary = _binary_path()
    if not binary.exists():
        print(
            f"wash binary not found at {binary}",
            file=sys.stderr,
        )
        sys.exit(1)
    args = [str(binary), *sys.argv[1:]]
    if sys.platform != "win32":
        os.execv(args[0], args)
    else:
        raise SystemExit(subprocess.call(args))
