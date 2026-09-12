"""Rebuild reference artifacts locally. This script never deploys or authenticates."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    for script in (
        ROOT / "scripts" / "build-rich-card-assets.py",
        ROOT / "exports" / "template" / "create_template.py",
        ROOT / "scripts" / "build-search-export-flow.py",
        ROOT / "scripts" / "build-rich-banner.py",
    ):
        subprocess.run([sys.executable, "-B", str(script)], cwd=ROOT, check=True)
    print("Built offline reference definition and blank templates; no deployment performed.")
