# Transparent Notes

A lightweight, transparent sticky notes application for Windows with system tray support. Perfect for keeping notes visible while working on other tasks.

## Features
- Transparent window with adjustable opacity (10% - 100%)
- System tray icon for quick access and management
- Customizable text color and size
- Always on top functionality
- Window position and settings persistence
- Minimalistic design
- Resizable window with drag handles
- Context menu for quick actions
- Keyboard shortcuts for common operations
- Automatic settings save and restore

## Usage
1. Double click `transparent_notes.exe` to start
2. Right-click for context menu with options:
   - Change text color
   - Adjust opacity
   - Toggle always on top
   - Reset window size
   - Exit application
3. Use system tray icon to:
   - Show/hide the note window
   - Access quick settings
   - Exit the application
4. Keyboard Shortcuts:
   - Ctrl + Plus: Increase font size
   - Ctrl + Minus: Decrease font size
   - Ctrl + H: Hide window
   - Ctrl + Q: Quick exit

## Building from Source

1. Clone the repository:
```bash
git clone https://github.com/utkarshshanu712/transparent-notes-pro.git
cd transparent-notes-pro
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Build the executable:
```bash
pyinstaller transparent_notes.spec
```

The executable will be created in the `dist` folder.

## Requirements
- Windows OS (Windows 10 or later recommended)
- Python 3.12+ (if building from source)
- Required packages:
  - pillow>=10.0.0
  - pystray>=0.19.4
  - pyinstaller>=6.0.0

## Development
- Written in Python using tkinter for GUI
- Uses pystray for system tray functionality
- Settings stored in AppData folder
- Modular code structure for easy maintenance

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Troubleshooting
- If the window becomes invisible, use the system tray icon to show it
- Settings are stored in `%APPDATA%/TransparentNotes/settings.json`
- For issues with transparency, ensure your Windows composition is enabled
- Check the system tray if the window is not visible

## License
See LICENSE file for details.

## Acknowledgments
- Icon design by [Author]
- Built with Python and tkinter
- Special thanks to contributors

## Version History
- v1.0.0 - Initial release
  - Basic functionality
  - System tray support
  - Settings persistence
- Future releases planned

## Contact
- GitHub Issues: [Project Issues](https://github.com/utkarshshanu712/transparent-notes-pro/issues)
- Email: utkarshshanu712@gmail.com