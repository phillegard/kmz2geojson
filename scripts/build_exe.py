#!/usr/bin/env python3
"""Build standalone executable using PyInstaller."""

import subprocess
import sys
from pathlib import Path


def main():
    """Build the executable."""
    project_root = Path(__file__).parent.parent
    spec_file = project_root / "kmz2geojson.spec"

    if not spec_file.exists():
        print(f"Error: {spec_file} not found")
        sys.exit(1)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"Using PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("Error: PyInstaller not installed.")
        print("Install it with: pip install pyinstaller")
        sys.exit(1)

    # Build command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file),
    ]

    print(f"Running: {' '.join(cmd)}")
    print(f"Working directory: {project_root}")
    print()

    result = subprocess.run(cmd, cwd=project_root)

    if result.returncode == 0:
        # Determine exe extension based on platform
        exe_name = "kmz2geojson.exe" if sys.platform == "win32" else "kmz2geojson"
        exe_path = project_root / "dist" / exe_name
        print()
        print("Build successful!")
        print(f"Executable: {exe_path}")
    else:
        print()
        print(f"Build failed with code {result.returncode}")
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
