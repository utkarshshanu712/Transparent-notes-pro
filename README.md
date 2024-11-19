# Transparent Notes

A lightweight, transparent sticky notes application for Windows with system tray support. Perfect for keeping notes visible while working on other tasks.

## Features
- Multiple tabs support with easy tab management
- Transparent window with adjustable opacity (10% - 100%)
- System tray icon for quick access and management
- Rich text formatting:
  - Text highlighting in multiple colors
  - Underline text with custom colors
  - Multiple font styles and sizes
- File operations:
  - Open text files (.txt, .py, etc.)
  - Save notes to files
  - Auto-save settings
- Window management:
  - Resizable with corner handles
  - Always on top functionality
  - Position memory
  - Auto-hiding title bar
- Customization:
  - Text color picker
  - 11 distinct font styles
  - Font sizes from 8pt to 72pt
  - Window opacity control

![Screenshot 2024-11-16 194126](https://github.com/user-attachments/assets/877df66a-4cd6-47b5-ba04-ea476fb0bdd6)
![Screenshot 2024-11-16 194226](https://github.com/user-attachments/assets/caadabe3-a68f-4869-b9dc-c1b9e449c33c)
![Screenshot 2024-11-16 194209](https://github.com/user-attachments/assets/b4d38024-0cdb-47a7-b52a-2bd690b3cb2e)
![Screenshot 2024-11-16 194151](https://github.com/user-attachments/assets/f6f7ec0e-5c9e-4819-96a4-cefd2a1d1d85)

## Keyboard Shortcuts
- Ctrl + N: New tab
- Ctrl + W: Close current tab
- Ctrl + O: Open file
- Ctrl + S: Save as
- Ctrl + Plus: Increase font size
- Ctrl + Minus: Decrease font size
- Ctrl + Q: Exit application

## Usage
1. Double click `transparent_notes.exe` to start
2. Right-click for context menu with options:
   - Text formatting (highlight, underline)
   - Font style and size
   - File operations
   - Tab management
3. Use system tray icon to:
   - Show/hide the note window
   - Quick exit
4. Mouse hover at top reveals title bar with:
   - Tab management
   - Window controls
   - Opacity settings
   - Color picker

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

## Antivirus Concerns

Some antivirus software may flag this application as suspicious due to how Python applications are packaged. This is a false positive. To resolve this:

1. The application is open source - you can review all code on GitHub
2. You can build from source yourself
3. Add an exclusion in Windows Defender:
   - Open Windows Security
   - Go to Virus & threat protection
   - Under Virus & threat protection settings, click "Manage settings"
   - Scroll to Exclusions and click "Add or remove exclusions"
   - Add the folder containing transparent_notes.exe
