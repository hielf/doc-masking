# 🔒 Python Backend Protection Guide

This document explains the different methods available to protect your Python backend code in the Doc Masking application.

## 🛡️ Protection Methods

### 1. PyInstaller (Recommended for most cases)
**Protection Level:** Good  
**Performance:** Good  
**File Size:** Medium  
**Dependencies:** None (standalone executable)

```bash
# Build with PyInstaller
npm run build:python
# or
python python_backend/build_executable.py
```

**Benefits:**
- Creates a single standalone executable
- No Python installation required on target machine
- Code is obfuscated and harder to reverse engineer
- Good performance

**Output:** `python_backend/dist/processor.exe`

### 2. Nuitka (Maximum Protection)
**Protection Level:** Excellent  
**Performance:** Excellent  
**File Size:** Small  
**Dependencies:** None (native executable)

```bash
# Build with Nuitka
npm run build:python:nuitka
# or
python python_backend/build_nuitka.py
```

**Benefits:**
- Compiles Python to C++ then to native machine code
- Extremely difficult to reverse engineer
- Best performance (native speed)
- Smallest file size
- No Python runtime required

**Output:** `python_backend/dist/processor.exe`

### 3. Encrypted Bytecode (Good Protection)
**Protection Level:** Good  
**Performance:** Good  
**File Size:** Small  
**Dependencies:** Python runtime + cryptography

```bash
# Build encrypted bytecode
npm run build:python:encrypt
# or
python python_backend/encrypt_bytecode.py
```

**Benefits:**
- Source code is compiled to bytecode and encrypted
- Requires encryption key to decrypt and run
- Good protection against casual inspection
- Small file size

**Output:** 
- `python_backend/processor_encrypted.py` (decryptor)
- `python_backend/processor_encrypted.bin` (encrypted bytecode)
- `python_backend/encryption.key` (encryption key)

## 🚀 Quick Start

### Option 1: Interactive Builder
```bash
python build_protected.py
```
This will show you a menu to choose your protection method.

### Option 2: Windows Batch File
```bash
build_protected.bat
```
Double-click this file on Windows for an easy build process.

### Option 3: NPM Scripts
```bash
# Build with PyInstaller
npm run build:protected

# Build with Nuitka
npm run build:protected:nuitka

# Build with encrypted bytecode
npm run build:protected:encrypt
```

## 📋 Complete Build Process

1. **Install Dependencies:**
   ```bash
   cd python_backend
   pip install -r requirements.txt
   cd ..
   ```

2. **Choose Protection Method:**
   - For maximum protection: Use Nuitka
   - For good protection with simplicity: Use PyInstaller
   - For encrypted bytecode: Use the encryption method

3. **Build Protected Backend:**
   ```bash
   python build_protected.py
   ```

4. **Build Electron App:**
   The build script will ask if you want to build the complete Electron app.

## 🔧 Manual Building

### PyInstaller
```bash
cd python_backend
python build_executable.py
cd ..
npm run build:win
```

### Nuitka
```bash
cd python_backend
python build_nuitka.py
cd ..
npm run build:win
```

### Encrypted Bytecode
```bash
cd python_backend
python encrypt_bytecode.py
cd ..
npm run build:win
```

## 📁 File Structure After Building

```
dist/
├── win-unpacked/
│   ├── Doc Masking.exe
│   └── python_backend/
│       ├── processor.exe          # PyInstaller/Nuitka executable
│       ├── processor_encrypted.py # Decryptor script
│       ├── processor_encrypted.bin # Encrypted bytecode
│       └── encryption.key         # Encryption key
```

## ⚠️ Important Notes

1. **Nuitka** provides the best protection but requires more build time
2. **PyInstaller** is the most reliable and widely used
3. **Encrypted bytecode** requires Python runtime on the target machine
4. Always test your protected builds before distribution
5. Keep your encryption keys secure if using the encrypted bytecode method

## 🛠️ Troubleshooting

### PyInstaller Issues
- Make sure all dependencies are installed
- Check that the source file has no syntax errors
- Try building with `--debug` flag for more information

### Nuitka Issues
- Install Visual Studio Build Tools on Windows
- Make sure you have enough disk space (Nuitka uses more during compilation)
- Check that all Python dependencies are available

### Encrypted Bytecode Issues
- Make sure cryptography library is installed
- Check that the encryption key file is not corrupted
- Verify that the encrypted file is not damaged

## 🔐 Security Considerations

1. **Nuitka** provides the highest level of protection
2. **PyInstaller** executables can still be reverse engineered with tools like `pyinstxtractor`
3. **Encrypted bytecode** is secure as long as the encryption key is protected
4. Consider using code obfuscation tools for additional protection
5. Never distribute source code alongside protected executables

## 📞 Support

If you encounter issues with any of the protection methods, check:
1. Python version compatibility
2. Required dependencies installation
3. Build tool versions
4. System permissions for file creation
