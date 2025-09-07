#!/usr/bin/env python3
"""
Build script for creating PumpkinScheduler executable
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    """Build the executable using PyInstaller"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    main_file = src_dir / "main.py"
    
    # Find PyInstaller in virtual environment
    venv_pyinstaller = project_root / ".venv" / "bin" / "pyinstaller"
    if not venv_pyinstaller.exists():
        # Try Windows path
        venv_pyinstaller = project_root / ".venv" / "Scripts" / "pyinstaller.exe"
    
    if not venv_pyinstaller.exists():
        print("❌ PyInstaller not found in virtual environment")
        print("💡 Run: pip install pyinstaller")
        return False
    
    # Ensure we're in the right directory
    os.chdir(project_root)
    
    # PyInstaller command with options
    cmd = [
        str(venv_pyinstaller),          # Use venv PyInstaller
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (GUI only)
        "--name=PumpkinScheduler",      # Executable name
        "--icon=icon.ico",              # Icon file (if exists)
        "--add-data=.env:.",           # Include .env file (Unix path separator)
        "--hidden-import=pystray._win32",  # Hidden imports for system tray
        "--hidden-import=pystray._darwin", 
        "--hidden-import=pystray._gtk",
        "--hidden-import=PIL._tkinter_finder",
        "--distpath=dist",              # Output directory
        "--workpath=build",             # Build directory
        "--specpath=.",                 # Spec file location
        str(main_file)                  # Main Python file
    ]
    
    # Remove icon flag if no icon file exists
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    print("🔨 Building PumpkinScheduler executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful!")
        
        # Show output location
        exe_path = project_root / "dist" / "PumpkinScheduler.exe"
        if not exe_path.exists():
            # Try without .exe for macOS/Linux
            exe_path = project_root / "dist" / "PumpkinScheduler"
        
        if exe_path.exists():
            print(f"📦 Executable created: {exe_path}")
            print(f"📏 File size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        
        # Clean up build files (optional)
        if os.getenv('CI'):
            # In CI, always clean up
            cleanup = 'y'
        else:
            cleanup = input("\n🧹 Clean up build files? (y/N): ").lower().strip()
        
        if cleanup == 'y':
            if os.path.exists("build"):
                shutil.rmtree("build")
            if os.path.exists("PumpkinScheduler.spec"):
                os.remove("PumpkinScheduler.spec")
            print("✅ Build files cleaned up!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False
    
    return True

def create_icon():
    """Create a simple icon file if it doesn't exist"""
    try:
        from PIL import Image, ImageDraw
        
        if not os.path.exists("icon.ico"):
            print("🎨 Creating icon file...")
            
            # Create a simple pumpkin icon
            size = 64
            image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Draw pumpkin
            draw.ellipse([8, 8, 56, 56], fill='darkorange', outline='black', width=2)
            # Eyes
            draw.ellipse([18, 22, 24, 28], fill='black')
            draw.ellipse([40, 22, 46, 28], fill='black')
            # Mouth
            draw.ellipse([28, 38, 36, 46], fill='black')
            
            # Save as ICO
            image.save("icon.ico", format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
            print("✅ Icon created: icon.ico")
            
    except ImportError:
        print("⚠️ PIL not available, skipping icon creation")
    except Exception as e:
        print(f"⚠️ Could not create icon: {e}")

if __name__ == "__main__":
    print("🎃 PumpkinScheduler Build Script")
    print("=" * 40)
    
    # Create icon if needed
    create_icon()
    
    # Build executable
    success = build_executable()
    
    if success:
        print("\n🎉 Build complete! Your executable is ready for distribution.")
        print("\n📋 Distribution Notes:")
        print("- The executable is standalone and doesn't require Python")
        print("- Users need to create their own .env file with FERNET_KEY")
        print("- Perfect for adding to Windows startup folder")
        print("- System tray functionality works on Windows/macOS/Linux")
    else:
        print("\n❌ Build failed. Check the error messages above.")
        sys.exit(1)
