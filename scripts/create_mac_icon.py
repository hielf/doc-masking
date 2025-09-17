#!/usr/bin/env python3
"""
Create macOS .icns icon from PNG files
"""

import os
import sys
import subprocess
from pathlib import Path

def check_iconutil():
    """Check if iconutil is available (macOS only)"""
    try:
        subprocess.run(["iconutil", "--help"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def create_iconset():
    """Create .iconset directory with required icon sizes"""
    iconset_dir = Path("build/icon.iconset")
    iconset_dir.mkdir(exist_ok=True)
    
    # Required icon sizes for macOS
    icon_sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png")
    ]
    
    # Use the highest resolution PNG as source
    source_icon = "build/icon-256.png"
    if not os.path.exists(source_icon):
        source_icon = "build/icon.png"
    
    if not os.path.exists(source_icon):
        print(f"❌ No source icon found. Please add icon.png or icon-256.png to build/")
        return False
    
    print(f"📁 Using {source_icon} as source icon")
    
    # Create resized icons
    for size, filename in icon_sizes:
        output_path = iconset_dir / filename
        try:
            # Use sips (macOS built-in) to resize images
            cmd = [
                "sips", "-z", str(size), str(size), 
                source_icon, "--out", str(output_path)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Created {filename} ({size}x{size})")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create {filename}: {e}")
            return False
    
    return True

def create_icns():
    """Convert .iconset to .icns file"""
    iconset_dir = "build/icon.iconset"
    icns_file = "build/icon.icns"
    
    try:
        cmd = ["iconutil", "-c", "icns", iconset_dir, "-o", icns_file]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ Created {icns_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create .icns file: {e}")
        return False

def cleanup_iconset():
    """Clean up temporary .iconset directory"""
    iconset_dir = "build/icon.iconset"
    if os.path.exists(iconset_dir):
        import shutil
        shutil.rmtree(iconset_dir)
        print("🧹 Cleaned up temporary .iconset directory")

def main():
    """Main function"""
    print("🍎 Creating macOS .icns icon...")
    
    # Check if we're on macOS
    if sys.platform != "darwin":
        print("❌ This script requires macOS (iconutil is not available on other platforms)")
        print("💡 Alternative: Use online converters or ask someone with macOS to create the .icns file")
        return False
    
    # Check if iconutil is available
    if not check_iconutil():
        print("❌ iconutil not found. This is required to create .icns files on macOS")
        return False
    
    # Create iconset directory with all required sizes
    if not create_iconset():
        return False
    
    # Convert to .icns
    if not create_icns():
        return False
    
    # Clean up
    cleanup_iconset()
    
    print("\n🎉 macOS icon created successfully!")
    print("📁 File: build/icon.icns")
    print("💡 You can now build your macOS app with: npm run build:mac")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
