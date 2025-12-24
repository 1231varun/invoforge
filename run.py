#!/usr/bin/env python3
"""
InvoForge - Development Server

Run with: python3 run.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

# Ensure output and data directories exist
(project_root / "output").mkdir(exist_ok=True)
(project_root / "data").mkdir(exist_ok=True)

from app import create_app

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  InvoForge - Professional Invoice Generator")
    print("=" * 50)
    print("\n  Open your browser at: http://127.0.0.1:5665\n")

    app = create_app()
    app.run(debug=True, port=5665)
