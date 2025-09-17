#!/usr/bin/env python3
"""
Encrypt Python bytecode for additional protection
"""

import os
import sys
import py_compile
import marshal
import zlib
import base64
from cryptography.fernet import Fernet
from pathlib import Path

def install_cryptography():
    """Install cryptography library if not already installed"""
    try:
        import cryptography
        print("Cryptography is already installed")
    except ImportError:
        print("Installing cryptography...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])

def generate_key():
    """Generate a new encryption key"""
    return Fernet.generate_key()

def save_key(key, key_file="encryption.key"):
    """Save encryption key to file"""
    with open(key_file, "wb") as f:
        f.write(key)
    print(f"🔑 Encryption key saved to {key_file}")

def load_key(key_file="encryption.key"):
    """Load encryption key from file"""
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            return f.read()
    else:
        key = generate_key()
        save_key(key, key_file)
        return key

def encrypt_python_file(input_file, output_file, key):
    """Encrypt a Python file to bytecode and encrypt it"""
    print(f"🔒 Encrypting {input_file}...")
    
    # Compile Python to bytecode
    bytecode_file = input_file.replace('.py', '.pyc')
    py_compile.compile(input_file, bytecode_file, doraise=True)
    
    # Read the bytecode
    with open(bytecode_file, 'rb') as f:
        # Skip the first 16 bytes (magic number, timestamp, size)
        bytecode_data = f.read()[16:]
    
    # Compress the bytecode
    compressed_data = zlib.compress(bytecode_data)
    
    # Encrypt the compressed data
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(compressed_data)
    
    # Encode as base64 for easier handling
    encoded_data = base64.b64encode(encrypted_data)
    
    # Write encrypted bytecode
    with open(output_file, 'wb') as f:
        f.write(encoded_data)
    
    # Clean up temporary bytecode file
    os.remove(bytecode_file)
    
    print(f"✅ Encrypted bytecode saved to {output_file}")

def create_decryptor_script(encrypted_file, key_file, output_script):
    """Create a script that can decrypt and execute the encrypted bytecode"""
    decryptor_code = f'''#!/usr/bin/env python3
"""
Decryptor and executor for encrypted Python bytecode
"""

import sys
import os
import base64
import zlib
import marshal
from cryptography.fernet import Fernet

def load_key(key_file="{key_file}"):
    """Load encryption key"""
    with open(key_file, "rb") as f:
        return f.read()

def decrypt_and_execute(encrypted_file="{encrypted_file}"):
    """Decrypt and execute the encrypted bytecode"""
    try:
        # Load key
        key = load_key()
        fernet = Fernet(key)
        
        # Read encrypted data
        with open(encrypted_file, 'rb') as f:
            encoded_data = f.read()
        
        # Decode from base64
        encrypted_data = base64.b64decode(encoded_data)
        
        # Decrypt
        compressed_data = fernet.decrypt(encrypted_data)
        
        # Decompress
        bytecode_data = zlib.decompress(compressed_data)
        
        # Execute the bytecode
        code_obj = marshal.loads(bytecode_data)
        exec(code_obj)
        
    except Exception as e:
        print(f"Error executing encrypted code: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    # Pass command line arguments to the decrypted script
    sys.argv = sys.argv[1:] if len(sys.argv) > 1 else []
    decrypt_and_execute()
'''
    
    with open(output_script, 'w') as f:
        f.write(decryptor_code)
    
    print(f"✅ Decryptor script created: {output_script}")

def main():
    """Main encryption process"""
    print("🔒 Encrypting Python backend...")
    
    # Install cryptography
    install_cryptography()
    
    # Generate or load key
    key = load_key()
    
    # Encrypt the processor
    encrypt_python_file("processor.py", "processor_encrypted.bin", key)
    
    # Create decryptor script
    create_decryptor_script("processor_encrypted.bin", "encryption.key", "processor_encrypted.py")
    
    print("\n✅ Encryption completed!")
    print("📁 Files created:")
    print("  - processor_encrypted.bin (encrypted bytecode)")
    print("  - processor_encrypted.py (decryptor script)")
    print("  - encryption.key (encryption key)")
    
    print("\n📋 Usage:")
    print("  python processor_encrypted.py <input_file> <output_file>")

if __name__ == "__main__":
    main()
