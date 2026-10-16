"""Compatibility entry point for the generated-site check."""

from pathlib import Path
import runpy
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.argv = [str(ROOT / "check.py"), "--site"]
runpy.run_path(str(ROOT / "check.py"), run_name="__main__")
