import tkinter as tk
from tkinter import colorchooser, filedialog
import json
import pystray
from PIL import Image, ImageTk
import threading
import os
import sys

class TransparentNotes:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.settings = self.load_settings()
        self.minimized = False
        
        # Initialize font size and create context menu before creating tabs
        self.current_font_size = self.settings.get('font_size', 10)
        self.text_opacity = 1.0
        self.create_context_menu()
        
        # Initialize variables before creating UI
        self.tab_counter = 0
        self.tabs = {}
        self.current_tab = None
        self.hide_timer = None
        self.start_x = None
        self.start_y = None
        
        # Create UI elements
        self.setup_ui()
        
        # Create system tray
        self.create_system_tray()
        
        # Add keyboard shortcuts
        self.root.bind('<Control-plus>', self.increase_font_size)
        self.root.bind('<Control-minus>', self.decrease_font_size)
        self.root.bind('<Control-s>', lambda e: self.save_as())
        self.root.bind('<Control-n>', lambda e: self.create_new_tab())
        self.root.bind('<Control-w>', lambda e: self.close_current_tab())
        self.root.bind('<Control-q>', lambda e: self.quit_app())
        self.root.bind('<Control-o>', lambda e: self.open_file())

    def setup_ui(self):
        """Setup all UI elements"""
        # Configure window
        self.root.configure(bg='black')
        self.root.attributes('-alpha', self.settings.get('opacity', 0.85))
        self.root.attributes('-topmost', True)
        self.root.geometry(self.settings.get('geometry', '400x300+100+100'))
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(fill='both', expand=True)
        
        # Create title bar
        self.title_bar = tk.Frame(self.main_frame, bg='black', height=25)
        self.title_bar.pack(fill='x', side='top')
        self.title_bar.pack_propagate(False)
        
        # Create tab frame and controls frame
        self.tab_frame = tk.Frame(self.title_bar, bg='black')
        self.tab_frame.pack(side='left', fill='x', expand=True)
        
        self.controls_frame = tk.Frame(self.title_bar, bg='black')
        self.controls_frame.pack(side='right', padx=5)
        
        # Create container for content
        self.container = tk.Frame(self.main_frame, bg='black')
        self.container.pack(fill='both', expand=True)
        
        # Create controls
        self.create_controls()
        
        # Bind movement events to title bar and its children
        self.title_bar.bind('<Button-1>', self.start_move)
        self.title_bar.bind('<B1-Motion>', self.on_move)
        self.title_bar.bind('<ButtonRelease-1>', self.stop_move)
        
        self.tab_frame.bind('<Button-1>', self.start_move)
        self.tab_frame.bind('<B1-Motion>', self.on_move)
        self.tab_frame.bind('<ButtonRelease-1>', self.stop_move)
        
        # Initially hide title bar
        self.title_bar.pack_forget()
        
        # Bind mouse motion for auto-hide
        self.root.bind('<Motion>', self.check_mouse_position)
        
        # Create resize handles
        self.create_resize_handles()
        
        # Create first tab
        self.create_new_tab()
        
        # Configure text area to maintain highlights
        text_area = self.tabs[self.current_tab]['text_area']
        text_area.bind('<<Selection>>', self.update_context_menu)

    def create_title_bar_contents(self):
        """Create organized title bar contents"""
        # Left section for tabs
        self.tab_frame = tk.Frame(self.title_bar, bg='black')
        self.tab_frame.pack(side='left', fill='x', expand=True)
        
        # Right section for controls
        self.controls_frame = tk.Frame(self.title_bar, bg='black')
        self.controls_frame.pack(side='right', padx=5)
        
        # Create controls
        self.create_controls()

    def create_controls(self):
        """Create organized window controls"""
        # Appearance controls
        self.color_btn = tk.Label(self.controls_frame, text='🎨', bg='black', fg='white', cursor='hand2')
        self.create_tooltip(self.color_btn, "Text Color")
        self.color_btn.pack(side='left', padx=3)
        self.color_btn.bind('<Button-1>', lambda e: self.choose_color())
        
        self.opacity_btn = tk.Label(self.controls_frame, text='👁', bg='black', fg='white', cursor='hand2')
        self.create_tooltip(self.opacity_btn, "Window Opacity")
        self.opacity_btn.pack(side='left', padx=3)
        
        # Create opacity submenu with more granular options
        self.opacity_menu = tk.Menu(self.root, tearoff=0)
        opacities = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        for opacity in opacities:
            self.opacity_menu.add_command(
                label=f"{int(opacity * 100)}%",
                command=lambda o=opacity: self.set_opacity(o)
            )
        self.opacity_btn.bind('<Button-1>', self.show_opacity_menu)
        
        # Separator
        tk.Label(self.controls_frame, text='|', bg='black', fg='gray').pack(side='left', padx=3)
        
        # Window controls
        self.min_btn = tk.Label(self.controls_frame, text='—', bg='black', fg='white', cursor='hand2')
        self.create_tooltip(self.min_btn, "Minimize to Tray")
        self.min_btn.pack(side='left', padx=3)
        self.min_btn.bind('<Button-1>', lambda e: self.minimize_to_tray())
        
        self.close_btn = tk.Label(self.controls_frame, text='✕', bg='black', fg='white', cursor='hand2')
        self.create_tooltip(self.close_btn, "Close (Ctrl+Q)")
        self.close_btn.pack(side='left', padx=3)
        self.close_btn.bind('<Button-1>', lambda e: self.quit_app())

    def start_move(self, event):
        """Begin window movement"""
        # Don't move if clicking controls
        if event.widget in self.controls_frame.winfo_children():
            return
        
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.initial_x = self.root.winfo_x()
        self.initial_y = self.root.winfo_y()

    def on_move(self, event):
        """Handle window movement"""
        if hasattr(self, 'start_x') and hasattr(self, 'start_y'):
            if self.start_x is not None and self.start_y is not None:
                # Calculate the distance moved
                dx = event.x_root - self.start_x
                dy = event.y_root - self.start_y
                
                # Set new position
                new_x = self.initial_x + dx
                new_y = self.initial_y + dy
                
                # Update window position
                self.root.geometry(f"+{new_x}+{new_y}")

    def stop_move(self, event):
        """Reset movement variables"""
        self.start_x = None
        self.start_y = None
        self.initial_x = None
        self.initial_y = None

    def create_context_menu(self):
        """Create enhanced right-click menu"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        
        # File operations
        self.context_menu.add_command(label="New Tab", command=self.create_new_tab, 
                                    accelerator="Ctrl+N")
        self.context_menu.add_command(label="Open File...", command=self.open_file, 
                                    accelerator="Ctrl+O")
        self.context_menu.add_command(label="Save As...", command=self.save_as, 
                                    accelerator="Ctrl+S")
        self.context_menu.add_separator()
        
        # Edit operations
        self.context_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate('<<Copy>>'),
                                    accelerator="Ctrl+C")
        self.context_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate('<<Paste>>'),
                                    accelerator="Ctrl+V")
        self.context_menu.add_separator()
        
        # Underline submenu
        underline_menu = tk.Menu(self.context_menu, tearoff=0)
        
        # Define underline colors (simplified to only solid style)
        underline_colors = {
            'Red': '#FF0000',
            'Blue': '#0000FF',
            'Green': '#00FF00',
            'Purple': '#800080',
            'Orange': '#FFA500'
        }
        
        # Create simple color options
        for color_name, color_code in underline_colors.items():
            underline_menu.add_command(
                label=color_name,
                command=lambda c=color_code: self.apply_underline(c)
            )
        
        # Add remove underline option
        underline_menu.add_separator()
        underline_menu.add_command(label="Remove Underline", command=self.remove_underline)
        
        self.context_menu.add_cascade(label="Underline", menu=underline_menu)
        
        # Highlight submenu
        highlight_menu = tk.Menu(self.context_menu, tearoff=0)
        colors = [
            ('Yellow', '#FFFF00'), ('Green', '#90EE90'), 
            ('Blue', '#ADD8E6'), ('Pink', '#FFB6C1'),
            ('Orange', '#FFB347'), ('Purple', '#E6E6FA'),
            ('None', 'none')
        ]
        for color_name, color_code in colors:
            highlight_menu.add_command(
                label=color_name,
                command=lambda c=color_code: self.highlight_text(c)
            )
        self.context_menu.add_cascade(label="Highlight", menu=highlight_menu)
        
        # Font style submenu with distinct, working fonts
        font_style_menu = tk.Menu(self.context_menu, tearoff=0)
        fonts = [
            ('Arial', 'Modern Sans-Serif'),
            ('Times New Roman', 'Classic Serif'),
            ('Courier New', 'Monospace'),
            ('Georgia', 'Elegant Serif'),
            ('Verdana', 'Clean Sans-Serif'),
            ('Tahoma', 'Clear Sans-Serif'),
            ('Consolas', 'Code Monospace'),
            ('Impact', 'Bold Display'),
            ('Palatino Linotype', 'Book Serif'),
            ('Trebuchet MS', 'Modern Sans-Serif'),
            ('Lucida Console', 'Terminal Monospace')
        ]
        
        for font_name, description in fonts:
            font_style_menu.add_command(
                label=f"{font_name} - {description}",
                command=lambda f=font_name: self.set_font_style(f)
            )
        self.context_menu.add_cascade(label="Font Style", menu=font_style_menu)
        
        # Font size submenu with more options
        font_size_menu = tk.Menu(self.context_menu, tearoff=0)
        sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 32, 36, 40, 48, 56, 64, 72]
        for size in sizes:
            font_size_menu.add_command(
                label=f"{size}pt",
                command=lambda s=size: self.set_font_size(s)
            )
        self.context_menu.add_cascade(label="Font Size", menu=font_size_menu)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Exit", command=self.quit_app, 
                                    accelerator="Ctrl+Q")

    def show_controls(self, event=None):
        if self.hide_timer:
            self.root.after_cancel(self.hide_timer)
            self.hide_timer = None
        
        self.controls_frame.pack(side='right')
        for tab_info in self.tabs.values():
            tab_info['label'].pack(side='left', padx=5)

    def schedule_hide(self, event=None):
        if self.hide_timer:
            self.root.after_cancel(self.hide_timer)
        self.hide_timer = self.root.after(1000, self.hide_controls)

    def hide_controls(self, event=None):
        x, y = self.root.winfo_pointerxy()
        widget_under_mouse = self.root.winfo_containing(x, y)
        
        if widget_under_mouse not in [self.title_bar] + list(self.controls_frame.winfo_children()):
            self.controls_frame.pack_forget()
            for tab_info in self.tabs.values():
                tab_info['label'].pack_forget()
        
        self.hide_timer = None

    def start_resize(self, event):
        """Begin window resizing"""
        self.resize_edge = event.widget.direction
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.start_width = self.root.winfo_width()
        self.start_height = self.root.winfo_height()
        self.start_pos_x = self.root.winfo_x()
        self.start_pos_y = self.root.winfo_y()

    def on_resize(self, event):
        """Handle window resizing"""
        if not hasattr(self, 'start_x'):
            return
        
        dx = event.x_root - self.start_x
        dy = event.y_root - self.start_y
        
        min_width = 200
        min_height = 100
        
        new_width = self.start_width
        new_height = self.start_height
        new_x = self.start_pos_x
        new_y = self.start_pos_y
        
        # Handle different resize edges
        if 'e' in self.resize_edge:
            new_width = max(min_width, self.start_width + dx)
        if 'w' in self.resize_edge:
            width_diff = min(dx, self.start_width - min_width)
            new_width = self.start_width - width_diff
            new_x = self.start_pos_x + width_diff
        if 's' in self.resize_edge:
            new_height = max(min_height, self.start_height + dy)
        if 'n' in self.resize_edge:
            height_diff = min(dy, self.start_height - min_height)
            new_height = self.start_height - height_diff
            new_y = self.start_pos_y + height_diff
        
        # Update window geometry
        self.root.geometry(f"{int(new_width)}x{int(new_height)}+{int(new_x)}+{int(new_y)}")

    def stop_resize(self, event):
        """Reset resize variables"""
        self.start_x = None
        self.start_y = None
        self.start_width = None
        self.start_height = None
        self.start_pos_x = None
        self.start_pos_y = None
        self.resize_edge = None

    def adjust_opacity(self, delta):
        """Adjust window opacity"""
        current = self.root.attributes('-alpha')
        new_opacity = max(0.1, min(1.0, current + delta))
        self.root.attributes('-alpha', new_opacity)
        self.settings['opacity'] = new_opacity

    def create_resize_grip(self):
        """Create resize grip in bottom right corner"""
        self.resize_grip = tk.Label(self.container, text='⟊', bg='black', fg='white', cursor='sizing')
        self.resize_grip.pack(side='right', anchor='se', padx=2, pady=2)
        self.resize_grip.bind('<Button-1>', self.start_resize)
        self.resize_grip.bind('<B1-Motion>', self.on_resize)

    def choose_color(self):
        """Open color picker and update text color"""
        color = colorchooser.askcolor(title="Choose Text Color")[1]
        if color:
            for tab_info in self.tabs.values():
                text_area = tab_info['text_area']
                text_area.config(fg=color, insertbackground=color)
            self.settings['text_color'] = color
            
            # Update controls color
            for widget in self.controls_frame.winfo_children():
                widget.config(fg=color)

    def save_settings(self):
        """Save current settings to file"""
        settings = {
            'opacity': self.root.attributes('-alpha'),
            'text_color': self.settings.get('text_color', 'white'),
            'font': self.settings.get('font', 'Arial'),
            'font_size': self.current_font_size,
            'geometry': self.root.geometry(),
            'tabs': {name: {'content': tab['text_area'].get('1.0', tk.END)} 
                    for name, tab in self.tabs.items()}
        }
        
        try:
            appdata_path = os.path.join(os.getenv('APPDATA'), 'TransparentNotes')
            os.makedirs(appdata_path, exist_ok=True)
            settings_file = os.path.join(appdata_path, 'settings.json')
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def create_tooltip(self, widget, text):
        """Create tooltip for widgets"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, bg='black', fg='white', relief='solid', borderwidth=1)
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind('<Leave>', lambda e: hide_tooltip())
            
        widget.bind('<Enter>', show_tooltip)

    def set_font_style(self, font_name):
        """Set font style for current text area"""
        if self.current_tab:
            text_area = self.tabs[self.current_tab]['text_area']
            text_area.configure(font=(font_name, self.current_font_size))
            self.settings['font'] = font_name
            
        # Update all tabs if desired
        for tab_info in self.tabs.values():
            tab_info['text_area'].configure(font=(font_name, self.current_font_size))

    def set_font_size(self, size):
        """Set specific font size"""
        self.current_font_size = size
        font_name = self.settings.get('font', 'Arial')
        
        # Update all tabs
        for tab_info in self.tabs.values():
            tab_info['text_area'].configure(font=(font_name, size))
        self.settings['font_size'] = size

    def increase_font_size(self, event=None):
        """Increase font size"""
        self.current_font_size = min(self.current_font_size + 2, 72)
        self.text_area.configure(font=('Arial', self.current_font_size))
        self.settings['font_size'] = self.current_font_size

    def decrease_font_size(self, event=None):
        """Decrease font size"""
        self.current_font_size = max(self.current_font_size - 2, 8)
        self.text_area.configure(font=('Arial', self.current_font_size))
        self.settings['font_size'] = self.current_font_size

    def load_settings(self):
        """Load settings from file"""
        default_settings = {
            'opacity': 0.85,
            'text_color': 'white',
            'text_opacity': 1.0,
            'font': 'Arial',
            'font_size': 10,
            'geometry': '400x300+100+100',
            'tabs': {}
        }
        
        try:
            appdata_path = os.path.join(os.getenv('APPDATA'), 'TransparentNotes')
            settings_file = os.path.join(appdata_path, 'settings.json')
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults to ensure all required settings exist
                    return {**default_settings, **settings}
            else:
                return default_settings
            
        except Exception as e:
            print(f"Error loading settings: {e}")
            return default_settings

    def run(self):
        """Start the application"""
        try:
            # Start system tray icon in separate thread
            self.icon_thread = threading.Thread(target=self.system_tray.run)
            self.icon_thread.daemon = True
            self.icon_thread.start()
            
            # Start main window
            self.root.mainloop()
            
        except Exception as e:
            print(f"Error running application: {e}")
            if hasattr(self, 'system_tray'):
                self.system_tray.stop()

    def create_new_tab(self, event=None):
        """Create a new tab with incremental naming"""
        # Find the next available tab number
        used_numbers = []
        for tab_name in self.tabs.keys():
            try:
                num = int(tab_name.split()[1])
                used_numbers.append(num)
            except (IndexError, ValueError):
                continue
        
        next_number = 1
        if used_numbers:
            used_numbers.sort()
            for i, num in enumerate(used_numbers, 1):
                if i != num:
                    next_number = i
                    break
            else:
                next_number = len(used_numbers) + 1
        
        tab_name = f"Note {next_number}"
        
        # Create tab label with close button
        tab_frame = tk.Frame(self.tab_frame, bg='black')
        tab_frame.pack(side='left', padx=2)
        
        tab_label = tk.Label(tab_frame, text=tab_name, bg='black', fg='white', 
                            cursor='hand2', padx=5)
        tab_label.pack(side='left')
        
        # Add close button to tab
        close_btn = tk.Label(tab_frame, text='×', bg='black', fg='white', 
                            cursor='hand2', padx=2)
        close_btn.pack(side='right')
        close_btn.bind('<Button-1>', lambda e, name=tab_name: self.close_tab(name))
        
        # Create content frame and text area
        content_frame = tk.Frame(self.container, bg='black')
        text_area = tk.Text(content_frame, wrap=tk.WORD, bg='black', fg='white',
                            insertbackground='white', relief='flat', padx=10, pady=5,
                            font=('Arial', self.current_font_size))
        text_area.pack(fill='both', expand=True)
        
        # Store tab information
        self.tabs[tab_name] = {
            'label': tab_label,
            'frame': content_frame,
            'text_area': text_area,
            'tab_frame': tab_frame,
            'close_btn': close_btn,
            'file_path': None,
            'number': next_number
        }
        
        # Bind events
        tab_label.bind('<Button-1>', lambda e, name=tab_name: self.select_tab(name))
        text_area.bind('<Button-3>', self.show_context_menu)
        
        # Select the new tab
        self.select_tab(tab_name)
        return tab_name

    def close_tab(self, tab_name):
        """Close specific tab"""
        if len(self.tabs) <= 1:  # Don't close last tab
            return
        
        # Get the tab number being closed
        closed_num = self.tabs[tab_name]['number']
        
        # Remove tab content and frame
        self.tabs[tab_name]['frame'].destroy()
        self.tabs[tab_name]['tab_frame'].destroy()
        
        # Select next appropriate tab before deleting
        remaining_tabs = sorted(
            [(name, info['number']) for name, info in self.tabs.items() if name != tab_name],
            key=lambda x: x[1]
        )
        
        # Find the next logical tab to select
        next_tab = None
        for name, num in remaining_tabs:
            if num > closed_num:
                next_tab = name
                break
        if not next_tab and remaining_tabs:
            next_tab = remaining_tabs[-1][0]
        
        # Delete the tab data
        del self.tabs[tab_name]
        
        # Select the next tab
        if next_tab:
            self.select_tab(next_tab)

    def select_tab(self, tab_name):
        """Select a tab and show its content"""
        # Hide current tab if exists
        if self.current_tab and self.current_tab in self.tabs:
            self.tabs[self.current_tab]['frame'].pack_forget()
            self.tabs[self.current_tab]['label'].configure(fg='white')
        
        # Show selected tab
        self.tabs[tab_name]['frame'].pack(fill='both', expand=True)
        self.tabs[tab_name]['label'].configure(fg='yellow')
        self.current_tab = tab_name
        self.text_area = self.tabs[tab_name]['text_area']

    def close_current_tab(self, event=None):
        """Close the current tab"""
        if len(self.tabs) <= 1:  # Don't close last tab
            return
        
        if self.current_tab:
            # Remove tab content and label
            self.tabs[self.current_tab]['frame'].destroy()
            self.tabs[self.current_tab]['label'].destroy()
            del self.tabs[self.current_tab]
            
            # Select another tab
            new_tab = list(self.tabs.keys())[0]
            self.select_tab(new_tab)

    def show_context_menu(self, event):
        """Show context menu at mouse position"""
        try:
            # Update text area reference before showing menu
            if event.widget.winfo_class() == 'Text':
                self.text_area = event.widget
            
            self.context_menu.post(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def create_tab_controls(self):
        """Create tab-related controls"""
        # Add new tab button
        self.new_tab_btn = tk.Label(self.controls_frame, text='+', bg='black', fg='white', cursor='hand2')
        self.create_tooltip(self.new_tab_btn, "New Tab (Ctrl+N)")
        self.new_tab_btn.pack(side='right', padx=5)
        self.new_tab_btn.bind('<Button-1>', lambda e: self.create_new_tab())
        
        # Add close tab button
        self.close_tab_btn = tk.Label(self.controls_frame, text='×', bg='black', fg='white', cursor='hand2')
        self.create_tooltip(self.close_tab_btn, "Close Tab (Ctrl+W)")
        self.close_tab_btn.pack(side='right', padx=5)
        self.close_tab_btn.bind('<Button-1>', lambda e: self.close_current_tab())

    def save_as(self):
        """Save current tab content to file"""
        if not self.current_tab:
            return
        
        # If file path exists, use it as initial directory
        initial_dir = None
        if self.tabs[self.current_tab].get('file_path'):
            initial_dir = os.path.dirname(self.tabs[self.current_tab]['file_path'])
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("All files", "*.*")
            ],
            initialdir=initial_dir
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    content = self.text_area.get('1.0', tk.END)
                    f.write(content)
                
                # Update tab name and file path
                file_name = os.path.basename(file_path)
                self.tabs[self.current_tab]['label'].configure(text=file_name)
                self.tabs[self.current_tab]['file_path'] = file_path
                
                # Update current tab name in tabs dictionary
                old_tab_name = self.current_tab
                self.tabs[file_name] = self.tabs.pop(old_tab_name)
                self.current_tab = file_name
                
            except Exception as e:
                print(f"Error saving file: {e}")

    def create_system_tray(self):
        """Create system tray icon"""
        # Create system tray menu
        menu = (
            pystray.MenuItem("Show", self.show_window),
            pystray.MenuItem("Hide", self.hide_window),
            pystray.MenuItem("Exit", self.quit_app)
        )
        
        # Create system tray icon
        try:
            # Try to load custom icon if available
            icon_path = os.path.join(os.path.dirname(__file__), 'notebook.ico')
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
            else:
                # Create a simple default icon
                image = Image.new('RGB', (64, 64), color='black')
        except Exception as e:
            print(f"Error loading icon: {e}")
            image = Image.new('RGB', (64, 64), color='black')
        
        self.system_tray = pystray.Icon(
            "transparent_notes",
            image,
            "Transparent Notes",
            menu
        )

    def quit_app(self, event=None):
        """Safely quit the application"""
        try:
            # Save settings before quitting
            self.save_settings()
            
            # Stop system tray icon
            if hasattr(self, 'system_tray'):
                self.system_tray.stop()
            
            # Destroy main window
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
            sys.exit(1)

    def minimize_to_tray(self, event=None):
        """Minimize window to system tray"""
        self.hide_window()

    def show_window(self):
        """Show the window from system tray"""
        self.root.deiconify()
        self.root.lift()
        self.minimized = False

    def hide_window(self):
        """Hide the window to system tray"""
        self.root.withdraw()
        self.minimized = True

    def open_file(self, event=None):
        """Open and load a file into a new tab"""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create new tab
                tab_name = os.path.basename(file_path)
                
                # Create tab label
                tab_frame = tk.Frame(self.tab_frame, bg='black')
                tab_frame.pack(side='left', padx=2)
                
                tab_label = tk.Label(tab_frame, text=tab_name, bg='black', fg='white', 
                                   cursor='hand2', padx=5)
                tab_label.pack(side='left')
                
                # Create content frame and text area
                content_frame = tk.Frame(self.container, bg='black')
                text_area = tk.Text(content_frame, wrap=tk.WORD, bg='black', fg='white',
                                   insertbackground='white', relief='flat', padx=10, pady=5,
                                   font=('Arial', self.current_font_size))
                text_area.pack(fill='both', expand=True)
                
                # Insert content
                text_area.insert('1.0', content)
                
                # Store tab information
                self.tabs[tab_name] = {
                    'label': tab_label,
                    'frame': content_frame,
                    'text_area': text_area,
                    'tab_frame': tab_frame,
                    'file_path': file_path
                }
                
                # Bind tab selection
                tab_label.bind('<Button-1>', lambda e, name=tab_name: self.select_tab(name))
                
                # Select the new tab
                self.select_tab(tab_name)
                
            except Exception as e:
                print(f"Error opening file: {e}")

    def create_resize_handles(self):
        """Create resize handles in corners only"""
        handle_size = 6  # Slightly larger corner handles
        
        # Create only corner resize handles
        self.corners = {
            'se': tk.Frame(self.root, bg='black', width=handle_size, height=handle_size),
            'sw': tk.Frame(self.root, bg='black', width=handle_size, height=handle_size),
            'ne': tk.Frame(self.root, bg='black', width=handle_size, height=handle_size),
            'nw': tk.Frame(self.root, bg='black', width=handle_size, height=handle_size)
        }
        
        # Configure handles
        for handle in self.corners.values():
            handle.pack_propagate(False)
        
        # Place corner handles
        self.corners['se'].place(relx=1, rely=1, anchor='se')
        self.corners['sw'].place(relx=0, rely=1, anchor='sw')
        self.corners['ne'].place(relx=1, rely=0, anchor='ne')
        self.corners['nw'].place(relx=0, rely=0, anchor='nw')
        
        # Bind resize events with direction info
        for pos, handle in self.corners.items():
            handle.direction = pos
            handle.bind('<Enter>', lambda e: e.widget.configure(bg='gray'))
            handle.bind('<Leave>', lambda e: e.widget.configure(bg='black'))
            handle.bind('<Button-1>', self.start_resize)
            handle.bind('<B1-Motion>', self.on_resize)
            handle.bind('<ButtonRelease-1>', self.stop_resize)

    def show_opacity_menu(self, event):
        """Show opacity menu under the opacity button"""
        self.opacity_menu.post(
            event.widget.winfo_rootx(),
            event.widget.winfo_rooty() + event.widget.winfo_height()
        )

    def set_opacity(self, value):
        """Set window opacity"""
        self.root.attributes('-alpha', value)
        self.settings['opacity'] = value

    def check_mouse_position(self, event):
        """Show/hide title bar based on mouse position"""
        title_bar_height = 25
        mouse_y = event.y_root - self.root.winfo_rooty()
        
        if mouse_y <= title_bar_height:
            self.show_title_bar()
        elif mouse_y > title_bar_height + 10:  # Add buffer zone
            self.schedule_hide_title_bar()

    def show_title_bar(self):
        """Show the title bar"""
        if self.hide_timer:
            self.root.after_cancel(self.hide_timer)
            self.hide_timer = None
        if not self.title_bar.winfo_ismapped():
            self.title_bar.pack(fill='x', side='top', before=self.container)

    def schedule_hide_title_bar(self, delay=1000):
        """Schedule hiding the title bar"""
        if self.hide_timer:
            self.root.after_cancel(self.hide_timer)
        self.hide_timer = self.root.after(delay, self.hide_title_bar)

    def hide_title_bar(self):
        """Hide the title bar"""
        x, y = self.root.winfo_pointerxy()
        widget_under_mouse = self.root.winfo_containing(x, y)
        
        # Check if mouse is over title bar or its children
        is_over_title = (widget_under_mouse and 
                        (widget_under_mouse == self.title_bar or 
                         widget_under_mouse in self.title_bar.winfo_children() or
                         any(widget_under_mouse in frame.winfo_children() 
                             for frame in [self.tab_frame, self.controls_frame])))
        
        if not is_over_title:
            self.title_bar.pack_forget()
        
        self.hide_timer = None

    def highlight_text(self, color):
        """Highlight selected text with specified color"""
        if self.current_tab:
            text_area = self.tabs[self.current_tab]['text_area']
            try:
                # Get selected text range
                sel_start = text_area.index("sel.first")
                sel_end = text_area.index("sel.last")
                
                # Remove existing highlight tags in selection
                for tag in text_area.tag_names():
                    if tag.startswith("highlight_"):
                        text_area.tag_remove(tag, sel_start, sel_end)
                
                # Apply new highlight if not 'none'
                if color != 'none':
                    tag_name = f"highlight_{color.replace('#', '')}"
                    text_area.tag_configure(tag_name, background=color)
                    text_area.tag_add(tag_name, sel_start, sel_end)
            except tk.TclError:
                # No text selected
                pass

    def update_context_menu(self, event):
        """Update context menu based on selected text"""
        if event.widget.winfo_class() == 'Text':
            self.text_area = event.widget
            try:
                has_selection = bool(self.text_area.get("sel.first", "sel.last"))
                state = 'normal' if has_selection else 'disabled'
                
                # Update menu states
                self.context_menu.entryconfig("Underline", state=state)
                self.context_menu.entryconfig("Highlight", state=state)
                
            except tk.TclError:
                # No selection
                self.context_menu.entryconfig("Underline", state='disabled')
                self.context_menu.entryconfig("Highlight", state='disabled')
        else:
            self.context_menu.entryconfig("Underline", state='disabled')
            self.context_menu.entryconfig("Highlight", state='disabled')

    def apply_underline(self, color):
        """Apply solid underline with specific color"""
        if self.current_tab:
            text_area = self.tabs[self.current_tab]['text_area']
            try:
                sel_start = text_area.index("sel.first")
                sel_end = text_area.index("sel.last")
                
                # Remove any existing underline tags
                for tag in text_area.tag_names():
                    if tag.startswith("underline_"):
                        text_area.tag_remove(tag, sel_start, sel_end)
                
                # Create unique tag name
                tag_name = f"underline_{color.replace('#', '')}"
                
                # Configure tag with solid underline style and color
                text_area.tag_configure(tag_name, 
                    underline=True,
                    underlinefg=color,
                    font=(self.settings.get('font', 'Arial'), self.current_font_size))
                
                # Apply the tag
                text_area.tag_add(tag_name, sel_start, sel_end)
                
            except tk.TclError:
                # No text selected
                pass

    def remove_underline(self):
        """Remove all underline styles from selected text"""
        if self.current_tab:
            text_area = self.tabs[self.current_tab]['text_area']
            try:
                sel_start = text_area.index("sel.first")
                sel_end = text_area.index("sel.last")
                
                # Remove all underline tags
                for tag in text_area.tag_names():
                    if tag.startswith("underline_"):
                        text_area.tag_remove(tag, sel_start, sel_end)
            except tk.TclError:
                # No text selected
                pass

if __name__ == "__main__":
    try:
        notes = TransparentNotes()
        notes.run()
    except Exception as e:
        print(f"Error starting application: {e}")
