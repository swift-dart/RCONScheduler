# 🎃 PumpkinScheduler - RCON Command Scheduler

A professional GUI application for scheduling and managing RCON commands across multiple Minecraft/Palworld servers with secure password encryption and modern interface design.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## ✨ Features

### 🔐 Security & Encryption
- **Auto-generated encryption keys** - no manual setup required
- **Fernet encryption** for secure password storage
- **Environment-based configuration** with automatic `.env` creation
- **Encrypted configuration files** for persistent storage

### 🖥️ Modern GUI Interface
- **Clean, intuitive design** with labeled sections and helpful placeholders
- **Real-time status indicators** for server connections (Green=Connected, Red=Failed, Gray=Not configured)
- **Visual feedback** with emojis and color-coded status messages
- **Keyboard navigation** support for accessibility
- **Responsive layout** with proper spacing and organization

### 🚀 Advanced Scheduling
- **User-friendly time selection** with intuitive dropdowns (no cron knowledge required!)
- **Smart time picker** with frequency options: Every Minute, 5/15/30 Minutes, Hourly, Daily, Weekly
- **Visual schedule preview** showing next execution time
- **Background task execution** with graceful shutdown
- **Multi-server command execution** with individual error handling

### 🔍 System Tray Integration
- **Minimize to system tray** for background operation
- **System tray icon** with right-click menu (Show/Hide/Quit)
- **Perfect for startup programs** - runs silently in background
- **Cross-platform support** for Windows, macOS, and Linux system trays

### 📊 Monitoring & Logging
- **Comprehensive logging** with timestamps and log levels
- **Real-time status updates** in the GUI status bar
- **Connection monitoring** with automatic reconnection attempts
- **Command execution feedback** with server responses

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd RCONScheduler
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (optional for development):**
   ```bash
   # For development only - production executables auto-generate keys
   echo "FERNET_KEY=$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')" > .env
   ```
   *Note: When running from source, encryption keys are auto-generated if missing*

5. **Run the application:**
   ```bash
   python src/main.py
   ```

## 📦 Executable Download (Recommended)

**Want a ready-to-use executable? No setup required!** 

👉 **[Download Latest Release](https://github.com/swift-dart/RCONScheduler/releases)** 👈

- ✅ **No Python installation required**
- ✅ **No manual key generation** - encryption keys auto-created
- ✅ **Standalone executable** for Windows/macOS/Linux  
- ✅ **Perfect for non-technical users**
- ✅ **Ready for system startup integration**

### Super Simple Setup
1. Download `PumpkinScheduler-[Platform].zip` for your OS
2. Extract and run `PumpkinScheduler`
3. **That's it!** Start configuring your servers immediately
4. Encryption keys are generated automatically on first run

## 📖 Usage Guide

### Server Configuration
1. **Server Details**: Enter your server details in the "🖥️ Server Configuration" section:
   - **Server Address**: Your server's IP or domain (e.g., `minecraft.example.com`)
   - **Port**: RCON port (typically `25575`)
   - **RCON Password**: Your server's RCON password

2. **Connection Status**: Watch the status indicators:
   - 🟢 **Green**: Successfully connected
   - 🔴 **Red**: Connection failed
   - ⚫ **Gray**: Not configured

3. **Reconnect**: Use the "🔌 Reconnect All" button to refresh connections

### Command Scheduling
1. **Command**: Enter the Minecraft/Palworld command (e.g., `say Hello World!`)
2. **Schedule Frequency**: Choose from easy dropdown options:
   - **Every Minute** - For testing or very frequent tasks
   - **Every 5/15/30 Minutes** - Regular maintenance intervals
   - **Hourly** - Specify which minute past the hour
   - **Daily** - Choose specific time (hour and minute)
   - **Weekly** - Pick day of week and time

3. **Time Selection**: 
   - For hourly: Select minute (0-59)
   - For daily/weekly: Select hour (00-23) and minute (00-59 in 5-minute intervals)
   - For weekly: Also select day of the week

4. **Schedule**: Click "📅 Schedule Command" to add the command to the scheduler
5. **Preview**: See the next execution time automatically calculated

### System Tray Operation
- **Minimize to Tray**: Close the window or minimize to hide to system tray
- **Background Operation**: Application continues running scheduled commands even when hidden
- **Restore Window**: Click the tray icon or right-click → "Show"
- **Complete Exit**: Right-click tray icon → "Quit"

### Time Selection Examples
Instead of cron expressions, simply choose from user-friendly options:

**Frequency Options:**
- **Every Minute** - Runs every single minute
- **Every 5 Minutes** - Runs at :00, :05, :10, :15, etc.
- **Every 15 Minutes** - Runs at :00, :15, :30, :45
- **Every 30 Minutes** - Runs at :00 and :30
- **Hourly** - Runs once per hour at specified minute
- **Daily** - Runs once per day at specified time
- **Weekly** - Runs once per week on specified day and time

**Time Examples:**
- Hourly at minute 30 → Runs at 1:30, 2:30, 3:30, etc.
- Daily at 14:30 → Runs every day at 2:30 PM
- Weekly on Friday at 18:00 → Runs every Friday at 6:00 PM

## 📁 Project Structure

```
RCONScheduler/
├── src/
│   └── main.py                    # Main application
├── docs/
│   ├── BUILD.md                   # Build instructions  
│   └── SETUP_INSTRUCTIONS.txt     # User setup guide
├── build_exe.py                   # Executable build script
├── create_release.py              # Release packaging script
├── requirements.txt               # Dependencies
├── example.env                    # Environment template
├── .gitignore                    # Git ignore file
└── README.md                     # This documentation
```

## 🏗️ Architecture

### Core Components
- **RCONServer**: Handles individual server connections with encryption
- **RCONScheduler**: Main GUI application with modern interface
- **Background Scheduler**: Cron-based task execution engine
- **Configuration Manager**: Encrypted config persistence

### Security Features
- Passwords encrypted with Fernet (AES 128 in CBC mode)
- Secure key storage in environment variables
- No plaintext password storage
- Encrypted configuration files

### GUI Components
- **CustomTkinter** for modern widget styling
- **Organized sections** with clear labels and headers
- **Status indicators** for visual feedback
- **Responsive design** with proper spacing

## 🔨 Building Executable (Optional)

**Most users should download pre-built executables from releases!**

### Pre-built Executables Available
- **Windows**: Auto-built via GitHub Actions
- **macOS**: Auto-built via GitHub Actions  
- **Linux**: Auto-built via GitHub Actions

### For Developers Only
```bash
# Install build dependencies
pip install pyinstaller

# Build executable manually
python build_exe.py

# Create release package  
python create_release.py
```

See [`docs/BUILD.md`](docs/BUILD.md) for detailed build instructions.

### Build Requirements
- Python 3.8+
- PyInstaller
- All project dependencies
- Virtual environment (recommended)

### Build Outputs
- **Executable**: `dist/PumpkinScheduler` (~22 MB)
- **Release Package**: `release/PumpkinScheduler-Release.zip`
- **Cross-platform**: Windows, macOS, Linux support

## 🆘 Support

If you encounter any issues:
1. Check the logs for error messages
2. Verify your server RCON configuration
3. Ensure your `.env` file contains a valid Fernet key
4. Open an issue on GitHub with detailed error information

Join the Discord for help: [Discord](https://discord.gg/Xh7BBYCGmn)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔄 Changelog

### v3.0.0 - User Experience Revolution
- ✅ **Auto-generated encryption keys** - zero manual setup required
- ✅ **Pre-built executables** for Windows, macOS, and Linux
- ✅ **User-friendly time selectors** replace complex cron expressions
- ✅ **System tray integration** for background operation
- ✅ **Minimize to tray** functionality for startup programs
- ✅ **Smart time picker** with frequency dropdowns and time selection
- ✅ **Real-time schedule preview** showing next execution
- ✅ **Cross-platform tray support** for Windows, macOS, and Linux
- ✅ **Perfect for production deployment** and automated server management

### v2.0.0 - Professional GUI Overhaul
- ✅ Modern, organized GUI with clear sections and labels
- ✅ Real-time status indicators for server connections
- ✅ Enhanced visual feedback with emojis and colors
- ✅ Improved error handling and user guidance
- ✅ Better keyboard navigation and accessibility
- ✅ Fernet encryption for secure password storage
- ✅ Comprehensive logging system replacing print statements
- ✅ Background task execution with graceful shutdown

### v1.0.0 - Initial Release
- ✅ Basic RCON server management for Minecraft/Palworld
- ✅ Cron-based command scheduling
- ✅ Multi-server support
- ✅ JSON configuration persistence

