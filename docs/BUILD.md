# PumpkinScheduler Executable Build

## Quick Build
```bash
python build_exe.py
```

## Manual Build
```bash
pyinstaller --onefile --windowed --name=PumpkinScheduler src/main.py
```

## Distribution Package Contents

### For End Users
1. **PumpkinScheduler.exe** (or PumpkinScheduler on macOS/Linux)
2. **setup_instructions.txt** 
3. **example.env** (template for users)

### Setup Instructions for Users
1. Download and run PumpkinScheduler.exe
2. Create a `.env` file in the same folder with:
   ```
   FERNET_KEY=your_generated_key_here
   ```
3. Generate a key by running this in Python:
   ```python
   from cryptography.fernet import Fernet
   print(Fernet.generate_key().decode())
   ```
4. Add to Windows startup folder for automatic background operation

## Build Requirements
- PyInstaller
- All project dependencies
- Python 3.8+

## File Sizes (Approximate)
- Windows: ~50-80 MB
- macOS: ~40-60 MB  
- Linux: ~40-70 MB

## System Tray Support
- ✅ Windows: Native system tray
- ✅ macOS: Menu bar integration
- ✅ Linux: System tray (with DE support)
