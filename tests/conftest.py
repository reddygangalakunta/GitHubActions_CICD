import sys
import os

# Add the project root (where app.py lives) to sys.path so
# "from app import app" works regardless of where pytest is invoked from.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
