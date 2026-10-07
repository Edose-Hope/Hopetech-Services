"""Vercel Python Function entrypoint. No secrets or database setup on import."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app
