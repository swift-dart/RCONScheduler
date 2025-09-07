#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script for creating PumpkinScheduler executable
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

# Set UTF-8 encoding for Windows compatibility
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def build_executable():
    """Build the executable using PyInstaller"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    main_file = src_dir / "main.py"
    
    # Check if we're in CI environment
    is_ci = os.getenv('CI') == 'true'
    
    # Find PyInstaller - check virtual environment first, then global
    pyinstaller_cmd = None
    
    if not is_ci:
        # Local development - try virtual environment first
        venv_pyinstaller = project_root / ".venv" / "bin" / "pyinstaller"
        if not venv_pyinstaller.exists():
            # Try Windows path
            venv_pyinstaller = project_root / ".venv" / "Scripts" / "pyinstaller.exe"
        
        if venv_pyinstaller.exists():
            pyinstaller_cmd = str(venv_pyinstaller)
    
    # If not found in venv or in CI, try global PyInstaller
    if pyinstaller_cmd is None:
        try:
            result = subprocess.run(['pyinstaller', '--version'], 
                                  capture_output=True, text=True, check=True)
            pyinstaller_cmd = 'pyinstaller'
            print(f"[OK] Found PyInstaller: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[ERROR] PyInstaller not found")
            print("[INFO] Run: pip install pyinstaller")
            return False
    
    # Ensure we're in the right directory
    os.chdir(project_root)
    
    # PyInstaller command with options
    cmd = [
        pyinstaller_cmd,                # Use found PyInstaller
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (GUI only)
        "--name=PumpkinScheduler",      # Executable name
        "--icon=icon.ico",              # Icon file (if exists)
        "--hidden-import=pystray._win32",  # Hidden imports for system tray
        "--hidden-import=pystray._darwin", 
        "--hidden-import=pystray._gtk",
        "--hidden-import=PIL._tkinter_finder",
        "--distpath=dist",              # Output directory
        "--workpath=build",             # Build directory
        "--specpath=.",                 # Spec file location
        str(main_file)                  # Main Python file
    ]
    
    # Add .env file if it exists (optional since app auto-generates it)
    if os.path.exists(".env"):
        # Use different path separators for different platforms
        if os.name == 'nt':  # Windows
            cmd.insert(-1, "--add-data=.env;.")
        else:  # Unix-like (Linux, macOS)
            cmd.insert(-1, "--add-data=.env:.")
    
    # Remove icon flag if no icon file exists
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    print("[BUILD] Building PumpkinScheduler executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("[OK] Build successful!")
        
        # Show output location
        exe_path = project_root / "dist" / "PumpkinScheduler.exe"
        if not exe_path.exists():
            # Try without .exe for macOS/Linux
            exe_path = project_root / "dist" / "PumpkinScheduler"
        
        if exe_path.exists():
            print(f"[INFO] Executable created: {exe_path}")
            print(f"[INFO] File size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        
        # Clean up build files (optional)
        if os.getenv('CI'):
            # In CI, always clean up
            cleanup = 'y'
        else:
            cleanup = input("\n[CLEANUP] Clean up build files? (y/N): ").lower().strip()
        
        if cleanup == 'y':
            if os.path.exists("build"):
                shutil.rmtree("build")
            if os.path.exists("PumpkinScheduler.spec"):
                os.remove("PumpkinScheduler.spec")
            print("[OK] Build files cleaned up!")
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build failed with error code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False
    
    return True

def create_icon():
    """Create a simple icon file if it doesn't exist"""
    try:
        from PIL import Image, ImageDraw
        
        if not os.path.exists("icon.ico"):
            print("[ICON] Creating icon file...")
            
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
            print("[OK] Icon created: icon.ico")
            
    except ImportError:
        print("[WARN] PIL not available, skipping icon creation")
    except Exception as e:
        print(f"[WARN] Could not create icon: {e}")

if __name__ == "__main__":
    print("PumpkinScheduler Build Script")
    print("=" * 40)
    
    # Create icon if needed
    create_icon()
    
    # Build executable
    success = build_executable()
    
    if success:
        print("\n[COMPLETE] Build complete! Your executable is ready for distribution.")
        print("\n[INFO] Distribution Notes:")
        print("- The executable is standalone and doesn't require Python")
        print("- Users need to create their own .env file with FERNET_KEY")
        print("- Perfect for adding to Windows startup folder")
        print("- System tray functionality works on Windows/macOS/Linux")
    else:
        print("\n[ERROR] Build failed. Check the error messages above.")
        sys.exit(1)
