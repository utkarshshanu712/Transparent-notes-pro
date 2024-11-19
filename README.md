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
- v2.0.0 (March 21, 2024)
  - Added multi-tab support with tab management
  - Implemented text highlighting and underline features
  - Added 11 distinct font styles
  - Enhanced font size control (8pt to 72pt)
  - Added file open/save functionality
  - Improved window management with corner resize handles
  - Added auto-hiding title bar
  - Enhanced context menu with formatting options
  - Added keyboard shortcuts
  - Improved settings persistence

- v1.0.0 (March 15, 2024)
  - Initial release
  - Basic note-taking functionality
  - System tray support
  - Window transparency control
  - Basic settings persistence
  - Simple text editing features

- Future Updates Planned:
  - Rich text formatting (bold, italic)
  - Spell check support
  - Cloud sync integration
  - Theme customization
  - Search functionality
  - Export to different formats

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
