#!/usr/bin/env python3
"""
InvoForge - Standalone Application Launcher
Opens the app in the default browser when run as an executable.
"""

import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path


def setup_paths():
    """Setup paths for PyInstaller bundle"""
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)

        os.environ["FLASK_TEMPLATE_PATH"] = str(base_path / "app" / "templates")
        os.environ["FLASK_STATIC_PATH"] = str(base_path / "static")

        env_example = base_path / ".env.example"
        user_data = Path.home() / ".invoforge"
        user_data.mkdir(exist_ok=True)

        user_env = user_data / ".env"
        if not user_env.exists() and env_example.exists():
            import shutil

            shutil.copy(env_example, user_env)

        os.environ["INVOFORGE_DATA"] = str(user_data)
        os.environ["DOTENV_PATH"] = str(user_env)


def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return False
        except OSError:
            return True


def is_invoforge_running(port: int) -> bool:
    """Check if InvoForge is already running on the port"""
    try:
        import urllib.request

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/settings", timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


def open_browser(port: int):
    """Open browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open(f"http://127.0.0.1:{port}")


def main():
    setup_paths()

    sys.path.insert(0, str(Path(__file__).parent))

    port = 5050

    # Check if port is already in use
    if is_port_in_use(port):
        # Check if it's InvoForge running
        if is_invoforge_running(port):
            print(f"\n{'=' * 50}")
            print("  InvoForge is already running!")
            print(f"{'=' * 50}")
            print(f"\n  Opening browser at: http://127.0.0.1:{port}\n")
            webbrowser.open(f"http://127.0.0.1:{port}")
            return
        else:
            # Port is used by something else, try alternative ports
            for alt_port in [5051, 5052, 5053, 5060, 5665]:
                if not is_port_in_use(alt_port):
                    print(f"  Port {port} is in use. Using port {alt_port} instead.\n")
                    port = alt_port
                    break
            else:
                print(f"\n  Error: Port {port} and alternatives are all in use.")
                print("  Please close other applications and try again.\n")
                input("  Press Enter to exit...")
                return

    from app import create_app

    app = create_app()

    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    print(f"\n{'=' * 50}")
    print("  InvoForge is running!")
    print(f"{'=' * 50}")
    print(f"\n  Open your browser at: http://127.0.0.1:{port}")
    print("\n  Press Ctrl+C to quit\n")

    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
