import PyInstaller.__main__
import os

# Get the absolute path to the icon file
icon_path = os.path.abspath('notebook.ico')

PyInstaller.__main__.run([
    'transparent_notes.py',
    '--onefile',
    '--windowed',
    '--icon', icon_path,
    '--add-data', f'{icon_path};.',
    '--name', 'transparent_notes',
    '--clean',
]) 