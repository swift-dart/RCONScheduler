import customtkinter as ctk
import mcrcon
import threading
import json
import tkinter as tk
from croniter import croniter
import time
import base64
from datetime import datetime, timezone
import logging
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
import pystray
from PIL import Image, ImageDraw
from functools import partial

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Load .env and Fernet key
load_dotenv()
FERNET_KEY = os.getenv('FERNET_KEY')

# Auto-generate Fernet key if it doesn't exist
if not FERNET_KEY:
    logging.info("No FERNET_KEY found in .env file. Generating new encryption key...")
    
    # Generate new key
    new_key = Fernet.generate_key().decode()
    
    # Create or update .env file
    env_file_path = '.env'
    env_content = f"FERNET_KEY={new_key}\n"
    
    # Read existing .env content if it exists
    existing_content = ""
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as f:
            existing_content = f.read()
    
    # Check if FERNET_KEY line already exists but is empty/commented
    if 'FERNET_KEY=' in existing_content:
        # Replace the existing line
        lines = existing_content.split('\n')
        updated_lines = []
        for line in lines:
            if line.startswith('FERNET_KEY=') or line.startswith('#FERNET_KEY='):
                updated_lines.append(f"FERNET_KEY={new_key}")
            else:
                updated_lines.append(line)
        env_content = '\n'.join(updated_lines)
    else:
        # Append to existing content
        if existing_content and not existing_content.endswith('\n'):
            existing_content += '\n'
        env_content = existing_content + f"FERNET_KEY={new_key}\n"
    
    # Write the .env file
    try:
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        logging.info(f"Created .env file with new encryption key")
        FERNET_KEY = new_key
        # Reload environment variables
        load_dotenv()
    except Exception as e:
        logging.error(f"Failed to create .env file: {e}")
        raise RuntimeError(f'Could not create .env file with encryption key: {e}')

if not FERNET_KEY:
    raise RuntimeError('Failed to set up encryption key!')

fernet = Fernet(FERNET_KEY)

class RCONServer:
    """
    Handles RCON server connection, authentication, and command execution.
    Passwords are stored encrypted using Fernet.
    """
    def __init__(self, address, port, password_enc):
        """
        Initialize RCONServer.
        :param address: Server address
        :param port: Server port
        :param password_enc: Encrypted password (Fernet)
        """
        self.address = address
        self.port = port
        # Store password as encrypted string
        self.password_enc = password_enc
        self.connected = False
        self.rcon_client = None

    @property
    def password(self):
        """
        Decrypt and return the server password.
        """
        return fernet.decrypt(self.password_enc.encode('utf-8')).decode('utf-8')

    def connect(self):
        """
        Connect to the RCON server using the provided credentials.
        """
        try:
            if not self.port.isdigit():
                raise ValueError("Port must be a number.")
            port_int = int(self.port)
            self.rcon_client = mcrcon.MCRcon(self.address, self.password, port=port_int)
            self.rcon_client.connect()
            self.connected = True
            logging.info(f"Connected to Server {self.address} via RCON")
        except ValueError as e:
            logging.error(f"Connection Error for {self.address}: {e}")
        except Exception as e:
            logging.error(f"Error connecting to Server {self.address} via RCON: {e}")
            self.connected = False

    def disconnect(self):
        """
        Disconnect from the RCON server.
        """
        if self.connected and self.rcon_client:
            try:
                self.rcon_client.disconnect()
                self.connected = False
                logging.info(f"Disconnected from Server {self.address}")
            except Exception as e:
                logging.error(f"Error disconnecting from Server {self.address}: {e}")

    def reconnect(self, retry_limit=3, retry_delay=5):
        """
        Attempt to reconnect to the RCON server with retries.
        :param retry_limit: Number of retry attempts
        :param retry_delay: Delay between attempts (seconds)
        """
        self.disconnect()  # Ensure we're starting fresh
        attempt = 0
        while attempt < retry_limit and not self.connected:
            attempt += 1
            logging.info(f"Reconnect attempt {attempt} for server {self.address}")
            time.sleep(retry_delay)
            self.connect()
            if self.connected:
                logging.info(f"Successfully reconnected to {self.address}")
                break
            else:
                logging.warning(f"Failed to reconnect to {self.address}, attempt {attempt} of {retry_limit}")

class RCONScheduler(ctk.CTk):
    """
    Main GUI application for scheduling and managing RCON server commands.
    """
    CONFIG_FILE = "server_config.json"

    def __init__(self):
        """
        Initialize the RCONScheduler GUI and load configuration.
        """
        super().__init__()
        self.title('🎃 PumpkinScheduler - RCON Command Scheduler')
        self.geometry('1000x800')
        self.minsize(900, 700)

        # System tray setup
        self.tray_icon = None
        self.is_minimized_to_tray = False
        
        # Protocol handler for window close/minimize
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Unmap>", self.on_minimize)

        self.rcon_servers = []
        self.setup_gui()
        self.load_config()
        self.connect_all_servers()
        self.start_background_task_execution()
        self.setup_system_tray()

    def setup_gui(self):
        """
        Set up the GUI layout, input fields, and status bar.
        """
        # Main container with padding
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Title
        title_label = ctk.CTkLabel(main_container, text="🎃 PumpkinScheduler - RCON Command Scheduler", 
                                 font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))

        # Server Configuration Section
        servers_section = ctk.CTkFrame(main_container)
        servers_section.pack(fill='x', pady=(0, 15))
        
        servers_title = ctk.CTkLabel(servers_section, text="🖥️ Server Configuration", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
        servers_title.pack(pady=(10, 10))
        
        # Column headers for server entries
        headers_frame = ctk.CTkFrame(servers_section)
        headers_frame.pack(fill='x', padx=15, pady=(0, 5))
        
        server_header = ctk.CTkLabel(headers_frame, text="Server Address", font=ctk.CTkFont(size=12, weight="bold"))
        server_header.pack(side='left', fill='x', expand=True, padx=5)
        port_header = ctk.CTkLabel(headers_frame, text="Port", font=ctk.CTkFont(size=12, weight="bold"))
        port_header.pack(side='left', fill='x', expand=True, padx=5)
        password_header = ctk.CTkLabel(headers_frame, text="RCON Password", font=ctk.CTkFont(size=12, weight="bold"))
        password_header.pack(side='left', fill='x', expand=True, padx=5)
        status_header = ctk.CTkLabel(headers_frame, text="Status", font=ctk.CTkFont(size=12, weight="bold"))
        status_header.pack(side='left', padx=5)

        self.server_entries = []
        self.server_status_labels = []
        
        # Create server entry rows with status indicators
        for i in range(9):
            frame = ctk.CTkFrame(servers_section)
            frame.pack(fill='x', padx=15, pady=2)

            address = ctk.CTkEntry(frame, placeholder_text=f"e.g., minecraft-server-{i+1}.com", 
                                 font=ctk.CTkFont(size=11))
            address.pack(side='left', fill='x', expand=True, padx=5)
            address.bind('<Return>', lambda e, idx=i: self.server_entries[(idx+1)%9][0].focus_set())
            
            port = ctk.CTkEntry(frame, placeholder_text="25575", width=80, 
                              font=ctk.CTkFont(size=11))
            port.pack(side='left', fill='x', expand=True, padx=5)
            port.bind('<Return>', lambda e, idx=i: self.server_entries[idx][2].focus_set())
            
            password = ctk.CTkEntry(frame, placeholder_text="Enter RCON password", show="*", 
                                  font=ctk.CTkFont(size=11))
            password.pack(side='left', fill='x', expand=True, padx=5)
            password.bind('<Return>', lambda e: self.command_entry.focus_set())
            
            # Status indicator
            status_label = ctk.CTkLabel(frame, text="●", text_color="gray", width=60)
            status_label.pack(side='left', padx=5)

            self.server_entries.append((address, port, password))
            self.server_status_labels.append(status_label)

        # Command Scheduling Section
        command_section = ctk.CTkFrame(main_container)
        command_section.pack(fill='x', pady=(0, 15))
        
        command_title = ctk.CTkLabel(command_section, text="⚡ Command Scheduling", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
        command_title.pack(pady=(10, 15))

        # Command input row
        command_input_frame = ctk.CTkFrame(command_section)
        command_input_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        command_label = ctk.CTkLabel(command_input_frame, text="Command:", 
                                   font=ctk.CTkFont(size=12, weight="bold"))
        command_label.pack(side='left', padx=(5, 10))
        
        self.command_entry = ctk.CTkEntry(command_input_frame, placeholder_text="e.g., say Hello World!", 
                                        font=ctk.CTkFont(size=11))
        self.command_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.command_entry.bind('<Return>', lambda e: self.frequency_dropdown.focus_set())

        # Time Selection Interface (replaces cron input)
        time_selection_frame = ctk.CTkFrame(command_section)
        time_selection_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        time_label = ctk.CTkLabel(time_selection_frame, text="Schedule:", 
                                font=ctk.CTkFont(size=12, weight="bold"))
        time_label.pack(side='left', padx=(5, 10))
        
        # Frequency selection
        self.frequency_dropdown = ctk.CTkComboBox(time_selection_frame, 
                                                values=["Every Minute", "Every 5 Minutes", "Every 15 Minutes", 
                                                       "Every 30 Minutes", "Hourly", "Daily", "Weekly"],
                                                width=150,
                                                command=self.on_frequency_change)
        self.frequency_dropdown.pack(side='left', padx=5)
        self.frequency_dropdown.set("Hourly")
        
        # Time selection (for daily/weekly schedules)
        self.time_frame = ctk.CTkFrame(time_selection_frame)
        self.time_frame.pack(side='left', padx=10)
        
        time_at_label = ctk.CTkLabel(self.time_frame, text="at", font=ctk.CTkFont(size=11))
        time_at_label.pack(side='left', padx=5)
        
        # Hour selection
        self.hour_dropdown = ctk.CTkComboBox(self.time_frame, 
                                           values=[f"{i:02d}" for i in range(24)],
                                           width=60,
                                           command=lambda x: self.update_schedule_preview())
        self.hour_dropdown.pack(side='left', padx=2)
        self.hour_dropdown.set("12")
        
        colon_label = ctk.CTkLabel(self.time_frame, text=":", font=ctk.CTkFont(size=12, weight="bold"))
        colon_label.pack(side='left')
        
        # Minute selection
        self.minute_dropdown = ctk.CTkComboBox(self.time_frame, 
                                             values=[f"{i:02d}" for i in range(0, 60, 5)],
                                             width=60,
                                             command=lambda x: self.update_schedule_preview())
        self.minute_dropdown.pack(side='left', padx=2)
        self.minute_dropdown.set("00")
        
        # Day selection (for weekly schedules)
        self.day_frame = ctk.CTkFrame(time_selection_frame)
        
        day_on_label = ctk.CTkLabel(self.day_frame, text="on", font=ctk.CTkFont(size=11))
        day_on_label.pack(side='left', padx=5)
        
        self.day_dropdown = ctk.CTkComboBox(self.day_frame, 
                                          values=["Monday", "Tuesday", "Wednesday", "Thursday", 
                                                 "Friday", "Saturday", "Sunday"],
                                          width=100,
                                          command=lambda x: self.update_schedule_preview())
        self.day_dropdown.pack(side='left', padx=5)
        self.day_dropdown.set("Monday")
        
        # Preview of generated schedule
        self.schedule_preview = ctk.CTkLabel(command_section, 
                                           text="", 
                                           font=ctk.CTkFont(size=10), 
                                           text_color="green")
        self.schedule_preview.pack(padx=15, pady=(5, 10))
        
        # Update visibility based on initial selection
        self.on_frequency_change("Hourly")

        # Action buttons
        button_frame = ctk.CTkFrame(command_section)
        button_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        self.schedule_button = ctk.CTkButton(button_frame, text="📅 Schedule Command", 
                                           font=ctk.CTkFont(size=12, weight="bold"),
                                           command=self.schedule_command)
        self.schedule_button.pack(side='left', padx=5)
        self.schedule_button.bind('<Return>', lambda e: self.schedule_command())
        
        self.connect_button = ctk.CTkButton(button_frame, text="🔌 Reconnect All", 
                                          font=ctk.CTkFont(size=12),
                                          command=self.connect_all_servers)
        self.connect_button.pack(side='left', padx=5)

        # Scheduled Commands Section
        commands_section = ctk.CTkFrame(main_container)
        commands_section.pack(fill='both', expand=True)
        
        commands_title = ctk.CTkLabel(commands_section, text="📋 Scheduled Commands", 
                                    font=ctk.CTkFont(size=16, weight="bold"))
        commands_title.pack(pady=(10, 10))

        # Commands listbox with better styling
        listbox_frame = ctk.CTkFrame(commands_section)
        listbox_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        self.scheduled_commands_listbox = tk.Listbox(listbox_frame, 
                                                   font=("Consolas", 10),
                                                   bg="#2b2b2b", fg="#ffffff",
                                                   selectbackground="#1f538d",
                                                   borderwidth=0)
        self.scheduled_commands_listbox.pack(fill='both', expand=True, padx=5, pady=5)

        # Status bar for connection and command execution feedback
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Configure your servers and schedule commands.")
        self.status_bar = tk.Label(self, textvariable=self.status_var, anchor='w', 
                                 bg='#1a1a1a', fg='#00ff00', font=("Consolas", 9),
                                 height=2)
        self.status_bar.pack(side='bottom', fill='x')

    def connect_all_servers(self):
        """
        Connect to all servers using the provided credentials in the GUI.
        """
        self.rcon_servers.clear()
        connected_count = 0
        for i, (address, port, password) in enumerate(self.server_entries):
            address_value, port_value, password_value = address.get(), port.get(), password.get()
            if address_value and port_value and password_value:
                # Encrypt password for storage and transmission
                password_enc = fernet.encrypt(password_value.encode('utf-8')).decode('utf-8')
                server = RCONServer(address_value, port_value, password_enc)
                server.connect()
                if server.connected:
                    self.rcon_servers.append(server)
                    connected_count += 1
                    # Update status indicator to green
                    self.server_status_labels[i].configure(text="●", text_color="green")
                else:
                    # Update status indicator to red
                    self.server_status_labels[i].configure(text="●", text_color="red")
            else:
                # Update status indicator to gray (no config)
                self.server_status_labels[i].configure(text="●", text_color="gray")
                if address_value or port_value or password_value:  # Partial config
                    logging.warning("Incomplete server details for server entry.")
        
        status_msg = f"Connected to {connected_count} server(s). Green=Connected, Red=Failed, Gray=Not configured"
        self.status_var.set(status_msg)

    def on_frequency_change(self, frequency):
        """
        Handle frequency dropdown changes and show/hide appropriate time selectors.
        """
        # Hide all time selection frames first
        self.time_frame.pack_forget()
        self.day_frame.pack_forget()
        
        if frequency in ["Daily"]:
            self.time_frame.pack(side='left', padx=10)
        elif frequency in ["Weekly"]:
            self.time_frame.pack(side='left', padx=10)
            self.day_frame.pack(side='left', padx=10)
        
        # Update the preview
        self.update_schedule_preview()
    
    def update_schedule_preview(self):
        """
        Update the schedule preview based on current selections.
        """
        try:
            cron_expr = self.generate_cron_from_ui()
            if cron_expr:
                next_run = croniter(cron_expr, datetime.now(timezone.utc)).get_next(datetime)
                preview_text = f"⏰ Next execution: {next_run.strftime('%Y-%m-%d %H:%M:%S')} UTC"
                self.schedule_preview.configure(text=preview_text, text_color="green")
            else:
                self.schedule_preview.configure(text="❌ Invalid schedule configuration", text_color="red")
        except Exception as e:
            self.schedule_preview.configure(text=f"❌ Error: {str(e)}", text_color="red")
    
    def generate_cron_from_ui(self):
        """
        Generate a cron expression from the user-friendly time selectors.
        """
        frequency = self.frequency_dropdown.get()
        hour = self.hour_dropdown.get()
        minute = self.minute_dropdown.get()
        day = self.day_dropdown.get()
        
        # Map day names to cron day numbers (0=Sunday, 1=Monday, etc.)
        day_mapping = {
            "Sunday": "0", "Monday": "1", "Tuesday": "2", "Wednesday": "3",
            "Thursday": "4", "Friday": "5", "Saturday": "6"
        }
        
        if frequency == "Every Minute":
            return "* * * * *"
        elif frequency == "Every 5 Minutes":
            return "*/5 * * * *"
        elif frequency == "Every 15 Minutes":
            return "*/15 * * * *"
        elif frequency == "Every 30 Minutes":
            return "*/30 * * * *"
        elif frequency == "Hourly":
            return f"{minute} * * * *"
        elif frequency == "Daily":
            return f"{minute} {hour} * * *"
        elif frequency == "Weekly":
            return f"{minute} {hour} * * {day_mapping.get(day, '1')}"
        else:
            return None

    def description_to_cron(self, description):
        """
        Convert human-readable description back to cron expression.
        This is a simplified conversion for the most common patterns.
        """
        if "Every Minute" in description:
            return "* * * * *"
        elif "Every 5 Minutes" in description:
            return "*/5 * * * *"
        elif "Every 15 Minutes" in description:
            return "*/15 * * * *"
        elif "Every 30 Minutes" in description:
            return "*/30 * * * *"
        elif "Hourly" in description:
            # Extract minute from description if possible
            if "at" in description:
                try:
                    time_part = description.split("at")[1].strip()
                    minute = time_part.split(":")[1]
                    return f"{minute} * * * *"
                except:
                    pass
            return "0 * * * *"  # Default to top of hour
        elif "Daily" in description:
            # Extract time from description
            if "at" in description:
                try:
                    time_part = description.split("at")[1].strip()
                    hour, minute = time_part.split(":")
                    return f"{minute} {hour} * * *"
                except:
                    pass
            return "0 12 * * *"  # Default to noon
        elif "Weekly" in description:
            # Extract day and time from description
            day_mapping = {
                "Sunday": "0", "Monday": "1", "Tuesday": "2", "Wednesday": "3",
                "Thursday": "4", "Friday": "5", "Saturday": "6"
            }
            try:
                if "on" in description and "at" in description:
                    day_part = description.split("on")[1].split("at")[0].strip()
                    time_part = description.split("at")[1].strip()
                    hour, minute = time_part.split(":")
                    day_num = day_mapping.get(day_part, "1")
                    return f"{minute} {hour} * * {day_num}"
            except:
                pass
            return "0 12 * * 1"  # Default to Monday noon
        else:
            return "0 * * * *"  # Default fallback

    def setup_system_tray(self):
        """
        Set up the system tray icon and menu.
        """
        # Create a simple icon
        def create_icon():
            width = height = 64
            image = Image.new('RGB', (width, height), color='orange')
            draw = ImageDraw.Draw(image)
            # Draw a simple pumpkin-like circle
            draw.ellipse([8, 8, 56, 56], fill='darkorange', outline='black', width=2)
            # Draw simple face
            draw.ellipse([18, 22, 24, 28], fill='black')  # Left eye
            draw.ellipse([40, 22, 46, 28], fill='black')  # Right eye
            draw.ellipse([28, 38, 36, 46], fill='black')  # Mouth
            return image

        # Create tray menu
        menu = pystray.Menu(
            pystray.MenuItem("Show", self.show_window, default=True),
            pystray.MenuItem("Hide", self.hide_to_tray),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.quit_app)
        )
        
        # Create tray icon
        self.tray_icon = pystray.Icon(
            "PumpkinScheduler",
            create_icon(),
            "🎃 PumpkinScheduler",
            menu
        )
        
        # Start tray icon in a separate thread
        tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        tray_thread.start()
    
    def show_window(self, icon=None, item=None):
        """
        Show the main window and bring it to front.
        """
        self.deiconify()
        self.lift()
        self.focus_force()
        self.is_minimized_to_tray = False
    
    def hide_to_tray(self, icon=None, item=None):
        """
        Hide the window to system tray.
        """
        self.withdraw()
        self.is_minimized_to_tray = True
    
    def on_minimize(self, event):
        """
        Handle window minimize event - hide to tray if minimized.
        """
        if event.widget == self and self.state() == 'iconic':
            self.after(100, self.hide_to_tray)  # Small delay to ensure proper minimize
    
    def on_closing(self):
        """
        Handle window closing - hide to tray instead of quitting.
        """
        self.hide_to_tray()
    
    def quit_app(self, icon=None, item=None):
        """
        Completely quit the application.
        """
        if self.tray_icon:
            self.tray_icon.stop()
        if hasattr(self, '_stop_event'):
            self._stop_event.set()
        self.quit()
        self.destroy()

    def schedule_command(self):
        """
        Schedule a command using the user-friendly time selectors.
        """
        command = self.command_entry.get()
        cron_expression = self.generate_cron_from_ui()
        
        if command and cron_expression:
            try:
                next_run = croniter(cron_expression, datetime.now(timezone.utc)).get_next(datetime)
                
                # Create a human-readable description
                frequency = self.frequency_dropdown.get()
                if frequency in ["Daily", "Weekly"]:
                    time_str = f"{self.hour_dropdown.get()}:{self.minute_dropdown.get()}"
                    if frequency == "Weekly":
                        description = f"{frequency} on {self.day_dropdown.get()} at {time_str}"
                    else:
                        description = f"{frequency} at {time_str}"
                else:
                    description = frequency
                
                display_text = f"📅 {command} | {description} | Next: {next_run.strftime('%Y-%m-%d %H:%M:%S')} UTC"
                self.scheduled_commands_listbox.insert(tk.END, display_text)
                self.status_var.set(f"✅ Scheduled '{command}' - {description}")
                logging.info(f"Scheduled command '{command}' with cron '{cron_expression}' for next run at {next_run} UTC")
                
                # Clear the command entry after successful scheduling
                self.command_entry.delete(0, tk.END)
                self.update_schedule_preview()
            except Exception as e:
                error_msg = f"❌ Error scheduling command: {str(e)}"
                self.status_var.set(error_msg)
                logging.error(error_msg)
        else:
            if not command:
                self.status_var.set("⚠️ Please enter a command")
            else:
                self.status_var.set("⚠️ Please select a valid schedule")

    def start_background_task_execution(self):
        """
        Start the background thread that checks and executes scheduled commands.
        """
        self._stop_event = threading.Event()
        
        def task_execution():
            while not self._stop_event.is_set():
                now = datetime.now(timezone.utc)
                for i in range(self.scheduled_commands_listbox.size()):
                    item = self.scheduled_commands_listbox.get(i)
                    # Handle new format: "📅 command | description | Next: timestamp UTC"
                    if " | " in item and " | Next: " in item:
                        parts = item.split(" | ")
                        command = parts[0].replace("📅 ", "")  # Remove emoji
                        description = parts[1]  # Human readable description
                        next_run_str = parts[2].replace("Next: ", "").replace(" UTC", "")
                        
                        # Convert description back to cron expression
                        # This is simplified - in a real implementation you might store the cron in the config
                        cron_expression = self.description_to_cron(description)
                    else:
                        # Fallback for old format
                        command, cron_expression, _ = item.rsplit(" - ", 2)
                        next_run_str = _.replace("Next run: ", "")
                    
                    try:
                        next_run = datetime.strptime(next_run_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                        if now >= next_run:
                            executed_count = 0
                            for server in self.rcon_servers:
                                if server.connected:
                                    server.disconnect()  # Disconnect before sending a new command
                                    server.reconnect()  # Reconnect
                                    try:
                                        response = server.rcon_client.command(command)
                                        msg = f"✅ Executed '{command}' on {server.address}. Response: {response}"
                                        logging.info(msg)
                                        self.status_var.set(msg)
                                        executed_count += 1
                                    except Exception as e:
                                        err_msg = f"❌ Error executing '{command}' on {server.address}: {e}"
                                        logging.error(err_msg)
                                        self.status_var.set(err_msg)
                                        server.reconnect()
                            
                            # Update the scheduled command with next run time
                            next_run = croniter(cron_expression, now).get_next(datetime)
                            self.scheduled_commands_listbox.delete(i)
                            self.scheduled_commands_listbox.insert(i, f"📅 {command} | {cron_expression} | Next: {next_run.strftime('%Y-%m-%d %H:%M:%S')} UTC")
                            
                            if executed_count > 0:
                                self.status_var.set(f"🚀 Command '{command}' executed on {executed_count} server(s)")
                    except Exception as e:
                        logging.error(f"Error processing scheduled command: {e}")
                self._stop_event.wait(60)

        self._task_thread = threading.Thread(target=task_execution, daemon=True)
        self._task_thread.start()

    def load_config(self):
        """
        Load server and scheduled command configuration from file.
        """
        try:
            with open(self.CONFIG_FILE, "r") as file:
                data = json.load(file)
                servers = data.get("servers", [])
                for i, server in enumerate(servers):
                    if i < len(self.server_entries):
                        self.server_entries[i][0].insert(0, server["address"])
                        self.server_entries[i][1].insert(0, server["port"])
                        # Passwords are now stored as encrypted, decrypt for GUI
                        try:
                            decoded_pw = fernet.decrypt(server["password_enc"].encode('utf-8')).decode('utf-8')
                        except Exception:
                            decoded_pw = server.get("password", "")
                        self.server_entries[i][2].insert(0, decoded_pw)
                commands = data.get("scheduled_commands", [])
                for command in commands:
                    self.schedule_command(command["command"], command["cron_expression"])
            logging.info("Configuration and scheduled commands loaded successfully.")
        except FileNotFoundError:
            logging.warning("Configuration file not found.")
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")

    def on_close(self):
        """
        Handle application close event: stop background thread, disconnect servers, and save config.
        """
        # Signal background thread to stop
        if hasattr(self, '_stop_event'):
            self._stop_event.set()
            if hasattr(self, '_task_thread'):
                self._task_thread.join(timeout=2)
        # Disconnect all servers
        for server in self.rcon_servers:
            try:
                server.disconnect()
            except Exception:
                pass
        self.save_config()
        self.destroy()

    def save_config(self):
        """
        Save server and scheduled command configuration to file.
        """
        scheduled_commands = []
        for item in self.scheduled_commands_listbox.get(0, tk.END):
            # Handle new format: "📅 command | cron_expression | Next: timestamp UTC"
            if " | " in item and " | Next: " in item:
                parts = item.split(" | ")
                command = parts[0].replace("📅 ", "")  # Remove emoji
                cron_expression = parts[1]
                scheduled_commands.append({"command": command, "cron_expression": cron_expression})
            else:
                # Fallback for old format
                try:
                    command, cron_expression = item.split(" - ")[:2]
                    scheduled_commands.append({"command": command, "cron_expression": cron_expression})
                except ValueError:
                    logging.warning(f"Could not parse scheduled command: {item}")
        
        config_data = {
            "servers": [
                {
                    "address": entry[0].get(),
                    "port": entry[1].get(),
                    # Store password as encrypted for best practice
                    "password_enc": fernet.encrypt(entry[2].get().encode('utf-8')).decode('utf-8') if entry[2].get() else ""
                }
                for entry in self.server_entries if entry[0].get() or entry[1].get() or entry[2].get()  # Only save non-empty entries
            ],
            "scheduled_commands": scheduled_commands
        }
        try:
            with open(self.CONFIG_FILE, "w") as file:
                json.dump(config_data, file, indent=4)
            logging.info("Configuration and scheduled commands saved successfully.")
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")

if __name__ == "__main__":
    app = RCONScheduler()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
