"""Build standalone .exe using PyInstaller."""

import subprocess
import sys


def main():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "runas-netonly",
        "--console",
        "--hidden-import", "tkinter",
        "--collect-submodules", "runas_netonly",
        "runas_netonly/__main__.py",
    ]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("\nDone. Output: dist/runas-netonly.exe")


if __name__ == "__main__":
    main()
