#!/usr/bin/env python3
"""
Build script to create a standalone executable using PyInstaller.
The app will open in the default browser when launched.
"""
import os
import subprocess
import sys
from pathlib import Path


def install_pyinstaller():
    print("Installing PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)


def build_app():
    project_root = Path(__file__).parent
    os.chdir(project_root)

    try:
        import PyInstaller
    except ImportError:
        install_pyinstaller()

    print("Building InvoForge application...")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "InvoForge",
        "--onedir",
        "--windowed",
        "--add-data", f"app/templates{os.pathsep}app/templates",
        "--add-data", f"static{os.pathsep}static",
        "--hidden-import", "flask",
        "--hidden-import", "docx",
        "--hidden-import", "num2words",
        "--hidden-import", "dotenv",
        "--hidden-import", "lxml",
        "--collect-all", "num2words",
        "launcher.py"
    ]

    # Add .env.example if it exists
    if Path(".env.example").exists():
        cmd.insert(-1, "--add-data")
        cmd.insert(-1, f".env.example{os.pathsep}.")

    subprocess.run(cmd, check=True)

    print("\nBuild complete!")
    print("Find your app at: dist/InvoForge/")

    if sys.platform == "darwin":
        print("\nTo create a macOS .app bundle, run:")
        print("  python3 build_app.py --app")


def build_macos_app():
    project_root = Path(__file__).parent
    os.chdir(project_root)

    try:
        import PyInstaller
    except ImportError:
        install_pyinstaller()

    print("Building InvoForge macOS app bundle...")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "InvoForge",
        "--onefile",
        "--windowed",
        "--add-data", f"app/templates{os.pathsep}app/templates",
        "--add-data", f"static{os.pathsep}static",
        "--add-data", f".env.example{os.pathsep}.",
        "--hidden-import", "flask",
        "--hidden-import", "docx",
        "--hidden-import", "num2words",
        "--hidden-import", "dotenv",
        "--collect-all", "num2words",
        "--icon", "NONE",
        "launcher.py"
    ]

    subprocess.run(cmd, check=True)

    print("\nmacOS app bundle created!")
    print("Find your app at: dist/InvoForge.app")


if __name__ == "__main__":
    if "--app" in sys.argv and sys.platform == "darwin":
        build_macos_app()
    else:
        build_app()
