#!/usr/bin/env python3
"""
Release preparation script for PumpkinScheduler
Creates distribution packages for different platforms
"""
import os
import shutil
import zipfile
from pathlib import Path

def create_release_package():
    """Create a release package for distribution"""
    
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist"
    release_dir = project_root / "release"
    
    # Clean and create release directory
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # Check if executable exists
    exe_file = dist_dir / "PumpkinScheduler"
    if not exe_file.exists():
        print("❌ Executable not found. Run build_exe.py first.")
        return False
    
    print("📦 Creating release package...")
    
    # Create release package contents
    package_dir = release_dir / "PumpkinScheduler"
    package_dir.mkdir()
    
    # Copy executable
    shutil.copy2(exe_file, package_dir / "PumpkinScheduler")
    
    # Copy documentation (optional - users don't need setup instructions anymore)
    # shutil.copy2(project_root / "docs" / "SETUP_INSTRUCTIONS.txt", package_dir)
    # shutil.copy2(project_root / "example.env", package_dir)
    
    # Create README for the package
    readme_content = """# 🎃 PumpkinScheduler - Ready to Run!

## 🚀 Quick Start
1. Run PumpkinScheduler (double-click the executable)
2. The application will automatically create encryption keys
3. Configure your servers and schedule commands!
4. Minimize to system tray for background operation

## ✨ Features
- ✅ **No setup required** - encryption keys auto-generated
- ✅ **User-friendly scheduling** - no cron knowledge needed
- ✅ **System tray support** - perfect for startup programs
- ✅ **Secure by design** - passwords encrypted automatically

## 🎮 Perfect For
- Minecraft server automation
- Palworld server management  
- Any RCON-compatible game server

## 🆘 Need Help?
- Visit: https://github.com/swift-dart/RCONScheduler
- Discord: https://discord.gg/Xh7BBYCGmn

Enjoy your automated server management! �
"""
    
    with open(package_dir / "README.txt", "w") as f:
        f.write(readme_content)
    
    # Create ZIP file
    zip_path = release_dir / "PumpkinScheduler-Release.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    # Calculate sizes
    exe_size = exe_file.stat().st_size / (1024 * 1024)
    zip_size = zip_path.stat().st_size / (1024 * 1024)
    
    print(f"✅ Release package created!")
    print(f"📁 Package location: {package_dir}")
    print(f"📦 ZIP file: {zip_path}")
    print(f"📏 Executable size: {exe_size:.1f} MB")
    print(f"📏 ZIP size: {zip_size:.1f} MB")
    
    print(f"\n📋 Package Contents:")
    for item in package_dir.iterdir():
        print(f"   - {item.name}")
    
    print(f"\n🚀 Ready for GitHub Release!")
    print(f"   1. Upload {zip_path.name} to GitHub Releases")
    print(f"   2. Tag as v3.0.0")
    print(f"   3. Include changelog in release notes")
    
    return True

if __name__ == "__main__":
    print("🎃 PumpkinScheduler Release Packager")
    print("=" * 40)
    
    success = create_release_package()
    if not success:
        exit(1)
