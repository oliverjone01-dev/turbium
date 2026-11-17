"""Compatibility command: build the canonical homepage, never recreate a preview."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parents[1]/'tools/build-home-v9.py'),run_name='__main__')
