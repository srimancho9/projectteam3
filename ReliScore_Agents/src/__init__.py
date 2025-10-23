from pathlib import Path
__all__ = ["version", "PACKAGE_ROOT"]

def version() -> str:
    return "ReliScore v0.1.0"

try:
    PACKAGE_ROOT = Path(__file__).resolve().parent
except NameError:
    PACKAGE_ROOT = Path.cwd() / "src" / "reli_core"
