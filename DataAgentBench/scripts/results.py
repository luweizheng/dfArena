"""Compatibility import; shared implementation lives in runners/results.py."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from runners.results import read, save, summarize, token_usage

__all__ = ['read', 'save', 'summarize', 'token_usage']
