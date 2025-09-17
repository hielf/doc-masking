#!/usr/bin/env python3
"""
Build script to compile Python backend using Nuitka for maximum obfuscation
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_nuitka():
    """Install Nuitka if not already installed"""
    try:
        import nuitka
        print("Nuitka is already installed")
    except ImportError:
        print("Installing Nuitka...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "nuitka"])

def build_with_nuitka():
    """Build the Python processor using Nuitka"""
    print("Building Python processor with Nuitka...")
    
    # Nuitka command with maximum obfuscation
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",  # Standalone executable
        "--onefile",  # Single file output
        "--assume-yes-for-downloads",  # Auto-download dependencies
        "--output-filename=processor.exe",  # Output filename
        "--output-dir=dist",  # Output directory
        "--remove-output",  # Clean up after build
        "--no-pyi-file",  # No .pyi files
        "--disable-console",  # No console window
        "--python-flag=-O",  # Python optimization
        "--python-flag=-OO",  # Extra optimization
        "--warn-unusual-code",  # Warn about unusual code
        "--warn-implicit-exceptions",  # Warn about implicit exceptions
        "--assume-yes-for-downloads",  # Auto-download
        "--plugin-enable=anti-bloat",  # Remove unused code
        "--static-libpython=no",  # Disable static libpython for pyenv compatibility
        "processor.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✅ Nuitka build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Nuitka build failed: {e}")
        return False

def main():
    """Main build process"""
    print("🔧 Building protected Python backend with Nuitka...")
    
    # Install Nuitka
    install_nuitka()
    
    # Build with Nuitka
    if build_with_nuitka():
        print("✅ Nuitka build completed successfully!")
        print("📁 Executable location: dist/processor.exe")
        
        print("\n📋 Benefits of Nuitka:")
        print("1. Compiles to C++ then to native machine code")
        print("2. Much harder to reverse engineer than PyInstaller")
        print("3. Better performance than interpreted Python")
        print("4. No Python runtime required on target machine")
    else:
        print("❌ Nuitka build failed. Check the error messages above.")

if __name__ == "__main__":
    main()
