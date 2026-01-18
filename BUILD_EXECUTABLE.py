"""
NeoCompression - Standalone Builder
Builds a standalone executable without requiring PATH modifications
"""

import subprocess
import sys
from pathlib import Path


def build_executable():
    """Build standalone executable using PyInstaller"""
    print("NeoCompression Standalone Builder")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 10):
        print(f"ERROR: Python 3.10+ required. You have {sys.version}")
        sys.exit(1)
    
    print(f"Python {sys.version} detected ✓")
    
    # Install PyInstaller if not present
    try:
        import PyInstaller
        print("PyInstaller found ✓")
    except ImportError:
        print("Installing PyInstaller...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to install PyInstaller: {result.stderr}")
            sys.exit(1)
        print("PyInstaller installed ✓")
    
    # Build the executable
    print("\nBuilding NeoCompression executable...")
    print("This may take a few minutes...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "NeoCompression",
        "--add-data", "neocompression;neocompression",
        "--noconsole",
        "--clean",
        "neocompression/gui.py"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("BUILD SUCCESSFUL!")
        print("=" * 50)
        
        exe_path = Path("dist") / "NeoCompression.exe"
        if exe_path.exists():
            print(f"\nExecutable created at:")
            print(f"  {exe_path.absolute()}")
            print(f"\nFile size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
            
            # Offer to copy to desktop
            response = input("\nCopy to Desktop? (y/n): ").lower()
            if response == 'y':
                desktop = Path.home() / "Desktop" / "NeoCompression.exe"
                exe_path.replace(desktop)
                print(f"Copied to: {desktop}")
        else:
            print("Build succeeded but executable not found in dist/")
    else:
        print("\nBUILD FAILED!")
        print("=" * 50)
        print("Error output:")
        print(result.stderr)
        sys.exit(1)


if __name__ == "__main__":
    build_executable()
