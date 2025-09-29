#!/usr/bin/env python3
"""
Master build script for creating protected Python backend
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print build banner"""
    print("=" * 60)
    print("[SECURE] DOC MASKING - PROTECTED PYTHON BACKEND BUILDER")
    print("=" * 60)
    print()

def show_menu():
    """Show build options menu"""
    print("Choose protection method:")
    print("1. PyInstaller (Good protection, single executable)")
    print("2. Nuitka (Maximum protection, native compilation)")
    print("3. Encrypted Bytecode (Good protection, requires Python runtime)")
    print("4. All methods (Build all three approaches)")
    print("5. Exit")
    print()

def build_pyinstaller():
    """Build using PyInstaller"""
    print("[BUILD] Building with PyInstaller...")
    try:
        os.chdir("python_backend")
        result = subprocess.run([sys.executable, "build_executable.py"], 
                              capture_output=True, text=True)
        os.chdir("..")
        
        if result.returncode == 0:
            print("[SUCCESS] PyInstaller build completed!")
            return True
        else:
            print(f"[ERROR] PyInstaller build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] PyInstaller build error: {e}")
        return False

def build_nuitka():
    """Build using Nuitka"""
    print("[BUILD] Building with Nuitka...")
    try:
        os.chdir("python_backend")
        result = subprocess.run([sys.executable, "build_nuitka.py"], 
                              capture_output=True, text=True)
        os.chdir("..")
        
        if result.returncode == 0:
            print("[SUCCESS] Nuitka build completed!")
            return True
        else:
            print(f"[ERROR] Nuitka build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Nuitka build error: {e}")
        return False

def build_encrypted():
    """Build encrypted bytecode"""
    print("[BUILD] Building encrypted bytecode...")
    try:
        os.chdir("python_backend")
        result = subprocess.run([sys.executable, "encrypt_bytecode.py"], 
                              capture_output=True, text=True)
        os.chdir("..")
        
        if result.returncode == 0:
            print("[SUCCESS] Encrypted bytecode build completed!")
            return True
        else:
            print(f"[ERROR] Encrypted bytecode build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Encrypted bytecode build error: {e}")
        return False

def build_electron():
    """Build Electron app with protected backend"""
    print("[BUILD] Building Electron app...")
    try:
        result = subprocess.run(["npm", "run", "build:win"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[SUCCESS] Electron app build completed!")
            return True
        else:
            print(f"[ERROR] Electron app build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Electron app build error: {e}")
        return False

def cleanup_build_files():
    """Clean up temporary build files"""
    print("[CLEANUP] Cleaning up build files...")
    
    cleanup_dirs = [
        "python_backend/build",
        "python_backend/__pycache__",
        "python_backend/dist"
    ]
    
    cleanup_files = [
        "python_backend/processor.spec",
        "python_backend/processor_encrypted.py",
        "python_backend/processor_encrypted.bin",
        "python_backend/encryption.key"
    ]
    
    for dir_path in cleanup_dirs:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"  Removed {dir_path}/")
    
    for file_path in cleanup_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"  Removed {file_path}")

def main():
    """Main build process"""
    print_banner()
    
    while True:
        show_menu()
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            if build_pyinstaller():
                print("\n[SUCCESS] PyInstaller build completed!")
                print("[INFO] Executable: python_backend/dist/processor.exe")
                print("[TIP] This executable is obfuscated and standalone")
            break
            
        elif choice == "2":
            if build_nuitka():
                print("\n[SUCCESS] Nuitka build completed!")
                print("[INFO] Executable: python_backend/dist/processor.exe")
                print("[TIP] This executable is compiled to native code")
            break
            
        elif choice == "3":
            if build_encrypted():
                print("\n[SUCCESS] Encrypted bytecode build completed!")
                print("[INFO] Files: processor_encrypted.py, processor_encrypted.bin, encryption.key")
                print("[TIP] This approach requires Python runtime but code is encrypted")
            break
            
        elif choice == "4":
            print("[BUILD] Building all protection methods...")
            success_count = 0
            
            if build_pyinstaller():
                success_count += 1
            if build_nuitka():
                success_count += 1
            if build_encrypted():
                success_count += 1
                
            print(f"\n[SUCCESS] Built {success_count}/3 protection methods")
            break
            
        elif choice == "5":
            print("[EXIT] Goodbye!")
            sys.exit(0)
            
        else:
            print("[ERROR] Invalid choice. Please enter 1-5.")
            print()
    
    # Ask if user wants to build Electron app
    build_electron_choice = input("\n[BUILD] Build Electron app with protected backend? (y/n): ").strip().lower()
    if build_electron_choice in ['y', 'yes']:
        if build_electron():
            print("\n[SUCCESS] Complete build finished!")
            print("[INFO] Check the 'dist' folder for your protected app")
        else:
            print("\n[ERROR] Electron build failed")
    
    # Ask if user wants to clean up
    cleanup_choice = input("\n[CLEANUP] Clean up temporary build files? (y/n): ").strip().lower()
    if cleanup_choice in ['y', 'yes']:
        cleanup_build_files()
    
    print("\n[SUCCESS] Build process completed!")

if __name__ == "__main__":
    main()
