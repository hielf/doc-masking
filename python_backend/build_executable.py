#!/usr/bin/env python3
"""
Build script to compile Python backend to executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("PyInstaller is already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_executable():
    """Build the Python processor as a standalone executable"""
    print("Building Python processor as executable...")
    
    # PyInstaller command with obfuscation options
    cmd = [
        "pyinstaller",
        "--onefile",  # Single executable file
        "--noconsole",  # No console window
        "--clean",  # Clean cache
        "--distpath", "dist",  # Output directory
        "--workpath", "build",  # Work directory
        "--specpath", ".",  # Spec file location
        "--name", "processor",  # Executable name
        "--add-data", "processor.py;.",  # Include source (optional)
        "--strip",  # Strip debug info
        "--optimize", "2",  # Python optimization level
        "processor.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("[SUCCESS] Executable built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build failed: {e}")
        return False

def cleanup_build_files():
    """Clean up temporary build files"""
    dirs_to_clean = ["build", "__pycache__"]
    files_to_clean = ["processor.spec"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned up {dir_name}/")
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Cleaned up {file_name}")

def main():
    """Main build process"""
    print("[BUILD] Building protected Python backend...")
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Build executable
    if build_executable():
        print("[SUCCESS] Build completed successfully!")
        print("[INFO] Executable location: dist/processor.exe")
        
        # Clean up
        cleanup_build_files()
        
        print("\n[INFO] Next steps:")
        print("1. The processor.exe is now compiled and obfuscated")
        print("2. Update your Electron app to use processor.exe instead of processor.py")
        print("3. The executable contains all dependencies and is much harder to reverse engineer")
    else:
        print("[ERROR] Build failed. Check the error messages above.")

if __name__ == "__main__":
    main()
