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
        
        # Configure window
        self.root.configure(bg='black')
        self.root.attributes('-alpha', 0.85)
        self.root.attributes('-topmost', True)
        self.root.geometry(self.settings['geometry'])
        
        # Create main container
        self.container = tk.Frame(self.root, bg='black')
        self.container.pack(fill='both', expand=True)
        
        # Create title bar first
        self.title_bar = tk.Frame(self.container, bg='black', height=20)
        self.title_bar.pack(fill='x', side='top')
        self.title_bar.bind('<Button-1>', self.start_move)
        self.title_bar.bind('<B1-Motion>', self.on_move)
        
        # Create controls frame
        self.controls_frame = tk.Frame(self.title_bar, bg='black')
        self.controls_frame.pack(side='right')
        
        # Add controls to the title bar
        self.create_controls()
        
        # Initialize text opacity with maximum brightness
        self.text_opacity = 1.0  # Set to maximum opacity
        
        # Initialize text area with the proper opacity
        self.current_font_size = self.settings.get('font_size', 10)
        initial_color = self.settings.get('text_color', 'white')
        
        # Set initial color to full brightness
        if initial_color == 'white':
            initial_color = '#FFFFFF'
        
        self.text_area = tk.Text(
            self.container,
            wrap=tk.WORD,
            font=('Arial', self.current_font_size),
            fg=initial_color,
            bg='black',
            borderwidth=0,
            highlightthickness=0,
            insertbackground=initial_color,
            relief='flat'
        )
        
        # Create resize frames (this will handle packing the text_area)
        self.create_resize_frames()
        
        # Create context menu
        self.create_context_menu()
        
        # Bind text area right-click
        self.text_area.bind('<Button-3>', self.show_context_menu)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-plus>', lambda e: self.increase_font_size())
        self.root.bind('<Control-minus>', lambda e: self.decrease_font_size())
        self.root.bind('<Control-equal>', lambda e: self.increase_font_size())
        
        # Bind mouse enter/leave events for controls
        self.title_bar.bind('<Enter>', self.show_controls)
        self.title_bar.bind('<Leave>', self.hide_controls)
        self.controls_frame.bind('<Enter>', self.show_controls)
        self.controls_frame.bind('<Leave>', self.hide_controls)
        
        # Initially hide controls
        self.controls_frame.pack_forget()
        
        # Add system tray icon
        self.create_system_tray()

    def create_system_tray(self):
        # Load icon from the executable's directory
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, 'notebook.ico')
        else:
            icon_path = 'notebook.ico'
        
        try:
            icon = Image.open(icon_path)
        except:
            # Fallback to a blank icon if the file is not found
            icon = Image.new('RGB', (32, 32), 'black')
        
        self.icon = pystray.Icon(
            "notes",
            icon,
            "Transparent Notes",
            menu=pystray.Menu(
                pystray.MenuItem("Show", self.show_window),
                pystray.MenuItem("Exit", self.quit_app)
            )
        )
        
        threading.Thread(target=self.icon.run, daemon=True).start()

    def show_window(self, icon=None):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_window(self):
        self.root.withdraw()

    def quit_app(self, icon=None):
        if hasattr(self, 'icon'):
            self.icon.stop()
        self.save_settings()
        self.root.quit()

    def create_controls(self):
        """Create all control buttons"""
        # Close button
        self.close_button = tk.Label(self.controls_frame, text='×', bg='black', fg='white', cursor='hand2')
        self.close_button.pack(side='right', padx=5)
        self.close_button.bind('<Button-1>', lambda e: self.quit_app())
        
        # Minimize button
        self.min_button = tk.Label(self.controls_frame, text='−', bg='black', fg='white', cursor='hand2')
        self.min_button.pack(side='right', padx=5)
        self.min_button.bind('<Button-1>', lambda e: self.hide_window())
        
        # Color button
        self.color_button = tk.Label(self.controls_frame, text='🎨', bg='black', fg='white', cursor='hand2')
        self.color_button.pack(side='right', padx=5)
        self.color_button.bind('<Button-1>', lambda e: self.choose_color())
        
        # Opacity controls
        self.opacity_up = tk.Label(self.controls_frame, text='🔆', bg='black', fg='white', cursor='hand2')
        self.opacity_up.pack(side='right', padx=5)
        self.opacity_up.bind('<Button-1>', lambda e: self.increase_opacity())
        
        self.opacity_down = tk.Label(self.controls_frame, text='🔅', bg='black', fg='white', cursor='hand2')
        self.opacity_down.pack(side='right', padx=5)
        self.opacity_down.bind('<Button-1>', lambda e: self.decrease_opacity())
        
        # Font size controls
        self.font_up = tk.Label(self.controls_frame, text='A+', bg='black', fg='white', cursor='hand2')
        self.font_up.pack(side='right', padx=5)
        self.font_up.bind('<Button-1>', lambda e: self.increase_font_size())
        
        self.font_down = tk.Label(self.controls_frame, text='A-', bg='black', fg='white', cursor='hand2')
        self.font_down.pack(side='right', padx=5)
        self.font_down.bind('<Button-1>', lambda e: self.decrease_font_size())

    def create_resize_frames(self):
        """Create resize handles at bottom and right edges"""
        # Create a frame to hold the text area and resize handles
        self.main_frame = tk.Frame(self.container, bg='black')
        self.main_frame.pack(expand=True, fill='both')
        
        # Text area (moved to main_frame)
        self.text_area.pack(in_=self.main_frame, expand=True, fill='both', padx=(0, 4), pady=(0, 4))
        
        # Bottom resize frame
        self.bottom_frame = tk.Frame(self.main_frame, bg='#333333', height=4, cursor='sb_v_double_arrow')
        self.bottom_frame.place(relx=0, rely=1.0, relwidth=1.0, height=4, anchor='sw')
        self.bottom_frame.bind('<Button-1>', self.start_resize)
        self.bottom_frame.bind('<B1-Motion>', self.resize_bottom)
        
        # Right resize frame
        self.right_frame = tk.Frame(self.main_frame, bg='#333333', width=4, cursor='sb_h_double_arrow')
        self.right_frame.place(relx=1.0, rely=0, relheight=1.0, width=4, anchor='ne')
        self.right_frame.bind('<Button-1>', self.start_resize)
        self.right_frame.bind('<B1-Motion>', self.resize_right)
        
        # Corner resize frame
        self.corner_frame = tk.Frame(self.main_frame, bg='#333333', width=6, height=6, cursor='sizing')
        self.corner_frame.place(relx=1.0, rely=1.0, width=6, height=6, anchor='se')
        self.corner_frame.bind('<Button-1>', self.start_resize)
        self.corner_frame.bind('<B1-Motion>', self.resize_corner)
        
        # Make sure text area is above resize handles for proper interaction
        self.text_area.lift()

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Save As...", command=self.save_text)
        self.context_menu.add_command(label="Clear", command=self.clear_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Choose Color", command=self.choose_color)
        self.context_menu.add_command(label="Increase Opacity", command=self.increase_opacity)
        self.context_menu.add_command(label="Decrease Opacity", command=self.decrease_opacity)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Increase Font Size (Ctrl+)", command=self.increase_font_size)
        self.context_menu.add_command(label="Decrease Font Size (Ctrl-)", command=self.decrease_font_size)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Exit", command=self.quit_app)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def bind_events(self):
        self.root.bind('<Control-s>', lambda e: self.save_text())
        self.root.bind('<Control-q>', lambda e: self.quit_app())

    def increase_opacity(self):
        current = self.root.attributes('-alpha')
        if current < 1.0:
            new_opacity = min(current + 0.1, 1.0)
            self.root.attributes('-alpha', new_opacity)
            self.settings['opacity'] = new_opacity

    def decrease_opacity(self):
        current = self.root.attributes('-alpha')
        if current > 0.1:
            new_opacity = max(current - 0.1, 0.1)
            self.root.attributes('-alpha', new_opacity)
            self.settings['opacity'] = new_opacity

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Text Color")[1]
        if color:
            self.text_area.config(fg=color, insertbackground=color)
            self.settings['text_color'] = color
            # Update controls color without resize button check
            for widget in self.controls_frame.winfo_children():
                widget.config(fg=color)

    def save_text(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.text_area.get('1.0', tk.END))

    def clear_text(self):
        self.text_area.delete('1.0', tk.END)

    def quit_app(self):
        if hasattr(self, 'icon'):
            self.icon.stop()
        self.save_settings()
        self.root.quit()

    def load_settings(self):
        default_settings = {
            'opacity': 0.85,
            'text_color': 'white',
            'text_opacity': 1.0,
            'font': 'Arial',
            'font_size': 10,
            'geometry': '400x300+100+100'
        }
        
        # Get AppData path
        appdata_path = os.path.join(os.getenv('APPDATA'), 'TransparentNotes')
        if not os.path.exists(appdata_path):
            os.makedirs(appdata_path)
        
        settings_file = os.path.join(appdata_path, 'settings.json')
        try:
            with open(settings_file, 'r') as f:
                return {**default_settings, **json.load(f)}
        except:
            return default_settings

    def save_settings(self):
        settings = {
            'opacity': self.root.attributes('-alpha'),
            'text_color': self.text_area.cget('fg'),
            'text_opacity': self.text_opacity,
            'font': 'Arial',
            'font_size': self.current_font_size,
            'geometry': self.root.geometry()
        }
        
        appdata_path = os.path.join(os.getenv('APPDATA'), 'TransparentNotes')
        settings_file = os.path.join(appdata_path, 'settings.json')
        try:
            with open(settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def run(self):
        self.root.mainloop()

    def start_resize(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.start_width = self.root.winfo_width()
        self.start_height = self.root.winfo_height()

    def resize_bottom(self, event):
        delta_y = event.y_root - self.start_y
        new_height = max(self.start_height + delta_y, 50)  # Reduced minimum height
        self.root.geometry(f"{self.root.winfo_width()}x{new_height}")

    def resize_right(self, event):
        delta_x = event.x_root - self.start_x
        new_width = max(self.start_width + delta_x, 100)  # Reduced minimum width
        self.root.geometry(f"{new_width}x{self.root.winfo_height()}")

    def resize_corner(self, event):
        delta_x = event.x_root - self.start_x
        delta_y = event.y_root - self.start_y
        new_width = max(self.start_width + delta_x, 100)  # Reduced minimum width
        new_height = max(self.start_height + delta_y, 50)  # Reduced minimum height
        self.root.geometry(f"{new_width}x{new_height}")

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def increase_font_size(self, event=None):
        self.current_font_size = min(self.current_font_size + 1, 72)
        self.text_area.configure(font=('Arial', self.current_font_size))
        self.settings['font_size'] = self.current_font_size

    def decrease_font_size(self, event=None):
        self.current_font_size = max(self.current_font_size - 1, 6)
        self.text_area.configure(font=('Arial', self.current_font_size))
        self.settings['font_size'] = self.current_font_size

    def show_controls(self, event=None):
        self.controls_frame.pack(side='right')

    def hide_controls(self, event=None):
        # Check if mouse is still over controls or title bar
        x, y = self.root.winfo_pointerxy()
        widget_under_mouse = self.root.winfo_containing(x, y)
        if widget_under_mouse not in [self.title_bar] + list(self.controls_frame.winfo_children()):
            self.controls_frame.pack_forget()

    def toggle_resize_mode(self, event=None):
        self.resize_mode = not self.resize_mode
        if self.resize_mode:
            self.resize_button.config(fg='yellow')  # Visual indicator that resize mode is active
        else:
            self.resize_button.config(fg=self.text_area.cget('fg'))

    def set_size(self, width, height):
        self.root.geometry(f"{width}x{height}")

    def on_drag(self, event):
        if self.resize_mode:
            # Get current window position and size
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            width = max(event.x + 10, 200)  # Minimum width of 200
            height = max(event.y + 10, 100)  # Minimum height of 100
            
            # Update window size
            self.root.geometry(f"{width}x{height}")

    def increase_window_opacity(self):
        current = self.root.attributes('-alpha')
        if current < 1.0:
            new_opacity = min(current + 0.1, 1.0)
            self.root.attributes('-alpha', new_opacity)
            self.settings['opacity'] = new_opacity

    def decrease_window_opacity(self):
        current = self.root.attributes('-alpha')
        if current > 0.1:
            new_opacity = max(current - 0.1, 0.1)
            self.root.attributes('-alpha', new_opacity)
            self.settings['opacity'] = new_opacity

if __name__ == "__main__":
    notes = TransparentNotes()
    notes.run()
