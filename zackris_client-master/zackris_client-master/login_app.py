import tkinter as tk
from tkinter import ttk, messagebox
import requests
import sys
from tkinter.font import Font
import keyboard
import mouse
import win32gui
import win32con
import win32api
import win32process
import threading
import os
import signal
import time
import ctypes
from datetime import datetime
import pytz

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class LogoutButton:
    def __init__(self, auth_token, on_logout_success, login_time, user_name):
        self.root = tk.Tk()
        self.root.title("")
        self.auth_token = auth_token
        self.on_logout_success = on_logout_success
        self.login_time = datetime.fromisoformat(login_time.replace('Z', '+00:00'))
        self.user_name = user_name
        self.stop_time_log = False

        # Make window floating and always on top
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)  # Remove window decorations

        # Create a frame with border
        self.frame = tk.Frame(self.root, borderwidth=1, relief='solid', cursor='fleur')
        self.frame.pack(fill='both', expand=True)

        # Create user label
        self.user_label = tk.Label(
            self.frame,
            text=f"Welcome, {self.user_name}",
            font=('Inter', 10),
            fg='#1e293b',  # slate-800
            cursor='fleur'
        )
        self.user_label.pack(padx=2, pady=(2, 0))

        # Create timer label
        self.timer_label = tk.Label(
            self.frame,
            text="00:00:00",
            font=('Inter', 10),
            fg='#475569',  # slate-600
            cursor='fleur'
        )
        self.timer_label.pack(padx=2, pady=(0, 2))

        # Create logout button
        self.logout_btn = tk.Button(
            self.frame,
            text="Logout",
            command=self.logout,
            font=('Inter', 11, 'bold'),
            bg='#ef4444',  # Red color
            fg='white',
            activebackground='#dc2626',  # Darker red
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5
        )
        self.logout_btn.pack(padx=2, pady=2)

        # Bind mouse events for dragging to all widgets
        for widget in [self.frame, self.user_label, self.timer_label]:
            widget.bind('<Button-1>', self.start_drag)
            widget.bind('<B1-Motion>', self.on_drag)

        # Position window in top-right corner
        screen_width = self.root.winfo_screenwidth()
        self.root.geometry(f'+{screen_width-200}+50')

        # Start timer update and time log update
        self.update_timer()
        self.update_time_log()

    def update_time_log(self):
        """Send time log update to API every minute"""
        if not self.stop_time_log:
            try:
                response = requests.post(
                    'https://monitoring-master-vzmgja.laravel.cloud/api/update-time-log',
                    headers={
                        'Authorization': f'Bearer {self.auth_token}',
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    }
                )

                if response.status_code != 200:
                    print(f"Failed to update time log: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"Error updating time log: {str(e)}")

            # Schedule next update in 60 seconds
            self.root.after(60000, self.update_time_log)

    def update_timer(self):
        """Update the timer display"""
        if not self.stop_time_log:  # Only update if not stopped
            now = datetime.now(pytz.UTC)
            duration = now - self.login_time

            # Calculate hours, minutes, seconds
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            # Update timer label
            self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")

            # Schedule next update
            self.root.after(1000, self.update_timer)

    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def on_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def logout(self):
        try:
            # Stop the time log updates
            self.stop_time_log = True

            response = requests.post(
                'https://monitoring-master-vzmgja.laravel.cloud/api/logout',
                headers={
                    'Authorization': f'Bearer {self.auth_token}',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            )

            if response.status_code == 200:
                self.root.destroy()
                self.on_logout_success()
            else:
                messagebox.showerror("Error", "Failed to logout. Please try again.")
                # If logout failed, resume time log updates
                self.stop_time_log = False

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
            # If logout failed, resume time log updates
            self.stop_time_log = False

    def run(self):
        self.root.mainloop()

class LoginApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("System Login")
        self.auth_token = None
        self.login_time = None
        self.user_name = None

        # Make it fullscreen and always on top
        self.root.attributes('-fullscreen', True, '-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.disable_close)

        # Disable Alt+F4 and Alt+Tab
        self.root.bind('<Alt-F4>', lambda e: 'break')
        self.root.bind('<Alt-Tab>', lambda e: 'break')
        self.root.bind('<Alt_L>', lambda e: 'break')
        self.root.bind('<Alt_R>', lambda e: 'break')
        self.root.bind('<Meta_L>', lambda e: 'break')  # Windows key
        self.root.bind('<Meta_R>', lambda e: 'break')  # Windows key

        # Tailwind-inspired colors
        self.colors = {
            'slate-900': '#0f172a',  # Background
            'slate-800': '#1e293b',  # Input background
            'slate-700': '#334155',  # Input focus
            'slate-50': '#f8fafc',   # Text color
            'indigo-600': '#4f46e5', # Primary button
            'indigo-700': '#4338ca', # Button hover
            'red-500': '#ef4444',    # Error color
            'red-600': '#dc2626',    # Error hover
        }

        # Set theme colors
        self.bg_color = self.colors['slate-900']
        self.fg_color = self.colors['slate-50']
        self.entry_bg = self.colors['slate-800']
        self.button_bg = self.colors['indigo-600']
        self.button_hover_bg = self.colors['indigo-700']

        self.root.configure(bg=self.bg_color)

        # Configure grid weight
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create styles
        self.style = ttk.Style()
        self.style.configure('Custom.TFrame', background=self.bg_color)
        self.style.configure('Custom.TLabel',
                           background=self.bg_color,
                           foreground=self.fg_color,
                           font=('Inter', 14))

        # Create main frame
        self.main_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Create title
        title_font = Font(family="Inter", size=32, weight="bold")
        title_label = tk.Label(self.main_frame,
                             text="System Login Required",
                             font=title_font,
                             bg=self.bg_color,
                             fg=self.fg_color)
        title_label.grid(row=0, column=0, pady=(100, 10))

        # Subtitle
        subtitle_font = Font(family="Inter", size=14)
        subtitle_label = tk.Label(self.main_frame,
                                text="Please enter your credentials to access the system",
                                font=subtitle_font,
                                bg=self.bg_color,
                                fg=self.colors['slate-700'])
        subtitle_label.grid(row=1, column=0, pady=(0, 50))

        # Create login frame with padding
        self.login_frame = ttk.Frame(self.main_frame, style='Custom.TFrame')
        self.login_frame.grid(row=2, column=0, ipadx=40, ipady=40)

        # Username
        ttk.Label(self.login_frame,
                 text="Username",
                 style='Custom.TLabel').grid(row=0, column=0, padx=5, pady=(0, 8), sticky='w')
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(self.login_frame,
                                     textvariable=self.username_var,
                                     font=('Inter', 13),
                                     bg=self.entry_bg,
                                     fg=self.fg_color,
                                     insertbackground=self.fg_color,
                                     relief='flat',
                                     width=35)
        self.username_entry.grid(row=1, column=0, padx=5, pady=(0, 20), ipady=8)

        # Password
        ttk.Label(self.login_frame,
                 text="Password",
                 style='Custom.TLabel').grid(row=2, column=0, padx=5, pady=(0, 8), sticky='w')
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(self.login_frame,
                                     textvariable=self.password_var,
                                     show="•",
                                     font=('Inter', 13),
                                     bg=self.entry_bg,
                                     fg=self.fg_color,
                                     insertbackground=self.fg_color,
                                     relief='flat',
                                     width=35)
        self.password_entry.grid(row=3, column=0, padx=5, pady=(0, 25), ipady=8)

        # Login button
        self.login_button = tk.Button(self.login_frame,
                                    text="Sign in",
                                    command=self.login,
                                    font=('Inter', 13, 'bold'),
                                    bg=self.button_bg,
                                    fg=self.fg_color,
                                    activebackground=self.button_hover_bg,
                                    activeforeground=self.fg_color,
                                    relief='flat',
                                    cursor='hand2',
                                    width=25,
                                    height=2)
        self.login_button.grid(row=4, column=0, pady=(0, 30))

        # Warning message
        warning_label = tk.Label(self.login_frame,
                               text="⚠️ System access is blocked until successful authentication",
                               font=('Inter', 12),
                               bg=self.bg_color,
                               fg=self.colors['red-500'])
        warning_label.grid(row=5, column=0, pady=(0, 10))

        # Bind events
        self.root.bind('<Key>', self.check_key)
        self.root.bind('<Return>', lambda e: self.login())

        # Bind focus events for visual feedback
        self.username_entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.username_entry.bind('<FocusOut>', self.on_entry_focus_out)
        self.password_entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.password_entry.bind('<FocusOut>', self.on_entry_focus_out)

        # Bind hover events for button
        self.login_button.bind('<Enter>', self.on_button_hover)
        self.login_button.bind('<Leave>', self.on_button_leave)

        # Initialize window handle after window is created
        self.root.after(100, self._initialize_window_handle)

        # Focus on username entry
        self.username_entry.focus()

    def _initialize_window_handle(self):
        """Initialize window handle after window is created"""
        try:
            self.hwnd = win32gui.GetParent(self.root.winfo_id())
            if self.hwnd:
                # Initialize blocking after window handle is set
                self._block_input_init()
                # Start topmost checking
                self.check_topmost()
        except Exception as e:
            print(f"Error initializing window handle: {e}")
            # Retry after a short delay
            self.root.after(100, self._initialize_window_handle)

    def _block_input_init(self):
        """Initialize input blocking with optimized performance"""
        try:
            # Block specific keys
            keyboard.block_key('alt')
            keyboard.block_key('alt gr')
            keyboard.block_key('left alt')
            keyboard.block_key('right alt')
            keyboard.block_key('windows')
            keyboard.block_key('left windows')
            keyboard.block_key('right windows')
            keyboard.block_key('tab')
            # Don't try to block combinations directly

            # Set up low-level keyboard hook
            keyboard.hook(self._handle_keyboard)
            # Set up low-level mouse hook
            mouse.hook(self._handle_mouse)

            # Start window focus checker thread
            self.stop_thread = False
            self.check_thread = threading.Thread(target=self._check_window_focus, daemon=True)
            self.check_thread.start()
        except Exception as e:
            print(f"Error initializing input blocking: {e}")

    def _handle_keyboard(self, event):
        """Handle keyboard events more efficiently"""
        try:
            # Block Alt and Windows keys and combinations
            blocked_keys = [
                'alt', 'alt gr', 'left alt', 'right alt',
                'windows', 'left windows', 'right windows',
                'tab', 'alt+tab', 'win+tab'
            ]

            if event.name in blocked_keys:
                return False

            # Allow input only when our window is focused
            if win32gui.GetForegroundWindow() == self.hwnd:
                return True
            return False
        except:
            return False

    def _handle_mouse(self, event):
        """Handle mouse events more efficiently"""
        try:
            cursor_pos = win32gui.GetCursorPos()
            window_rect = win32gui.GetWindowRect(self.hwnd)

            if (window_rect[0] <= cursor_pos[0] <= window_rect[2] and
                window_rect[1] <= cursor_pos[1] <= window_rect[3]):
                return True
            return False
        except:
            return False

    def _check_window_focus(self):
        """Check window focus with reduced frequency"""
        while not self.stop_thread:
            try:
                if win32gui.GetForegroundWindow() != self.hwnd:
                    win32gui.SetForegroundWindow(self.hwnd)
                time.sleep(0.2)  # Check every 200ms instead of continuously
            except Exception as e:
                print(f"Error in focus check: {e}")
                time.sleep(0.2)

    def check_topmost(self):
        """Ensure window stays on top with reduced frequency"""
        try:
            if hasattr(self, 'hwnd') and self.hwnd:
                win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        except Exception as e:
            print(f"Error setting window topmost: {e}")

        # Check less frequently (every 500ms instead of 100ms)
        self.root.after(500, self.check_topmost)

    def disable_close(self):
        """Prevent window from being closed"""
        pass

    def on_entry_focus_in(self, event):
        event.widget.configure(bg=self.colors['slate-700'])

    def on_entry_focus_out(self, event):
        event.widget.configure(bg=self.entry_bg)

    def on_button_hover(self, event):
        self.login_button.configure(bg=self.button_hover_bg)

    def on_button_leave(self, event):
        self.login_button.configure(bg=self.button_bg)

    def check_key(self, event):
        # Block Alt and Windows keys and combinations
        blocked_keys = ['Alt_L', 'Alt_R', 'Meta_L', 'Meta_R', 'Tab']
        if event.keysym in blocked_keys:
            return 'break'

        # Allow alphanumeric, symbols, navigation keys, and function keys
        allowed_keys = ['Return', 'BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down',
                       'Home', 'End', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R']
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}\\|;:\'",.<>/?`~ ')

        if event.keysym in allowed_keys:
            return

        if event.char and event.char not in allowed_chars:
            return 'break'

    def show_logout_button(self):
        """Show the floating logout button"""
        self.root.withdraw()  # Hide login window
        logout_btn = LogoutButton(self.auth_token, self.on_logout, self.login_time, self.user_name)
        logout_btn.run()

    def on_logout(self):
        """Handle successful logout"""
        self.auth_token = None
        self.root.deiconify()  # Show login window again
        self.password_var.set("")  # Clear password field
        self.username_entry.focus()

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        try:
            response = requests.post(
                'https://monitoring-master-vzmgja.laravel.cloud/api/login',
                json={
                    'username': username,
                    'password': password
                }
            )

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    # Store the authentication token and user data
                    data = response_data.get('data', {})
                    self.auth_token = data.get('token')
                    self.login_time = data.get('login_at')
                    self.user_name = data.get('name')

                    if self.auth_token and self.login_time and self.user_name:
                        # Clean up input blocking if running as admin
                        if is_admin():
                            self.stop_thread = True
                            keyboard.unhook_all()
                            mouse.unhook_all()
                        # Show the logout button
                        self.show_logout_button()
                    else:
                        messagebox.showerror("Error", "Incomplete login data in response")
                else:
                    messagebox.showerror("Error", response_data.get('message', 'Login failed'))
            else:
                messagebox.showerror("Error", "Invalid username or password")
                self.password_var.set("")  # Clear password field
                self.password_entry.focus()

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
        except ValueError as e:
            messagebox.showerror("Error", "Invalid response format from server")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = LoginApp()
    app.run()