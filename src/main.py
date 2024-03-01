import customtkinter as ctk
import mcrcon
import threading
import json
import tkinter as tk
from croniter import croniter
import datetime
import time

class RCONServer:
    def __init__(self, address, port, password):
        self.address = address
        self.port = port
        self.password = password
        self.connected = False
        self.rcon_client = None

    def connect(self):
        try:
            if not self.port.isdigit():
                raise ValueError("Port must be a number.")
            port_int = int(self.port)
            self.rcon_client = mcrcon.MCRcon(self.address, self.password, port=port_int)
            self.rcon_client.connect()
            self.connected = True
            print(f"Connected to Server {self.address} via RCON")
        except ValueError as e:
            print(f"Connection Error for {self.address}: {e}")
        except Exception as e:
            print(f"Error connecting to Server {self.address} via RCON: {e}")
            self.connected = False

    def disconnect(self):
        if self.connected and self.rcon_client:
            try:
                self.rcon_client.disconnect()
                self.connected = False
                print(f"Disconnected from Server {self.address}")
            except Exception as e:
                print(f"Error disconnecting from Server {self.address}: {e}")

    def reconnect(self, retry_limit=3, retry_delay=5):
        self.disconnect()  # Ensure we're starting fresh
        attempt = 0
        while attempt < retry_limit and not self.connected:
            attempt += 1
            print(f"Reconnect attempt {attempt} for server {self.address}")
            time.sleep(retry_delay)
            self.connect()
            if self.connected:
                print(f"Successfully reconnected to {self.address}")
                break
            else:
                print(f"Failed to reconnect to {self.address}, attempt {attempt} of {retry_limit}")

class RCONScheduler(ctk.CTk):
    CONFIG_FILE = "server_config.json"

    def __init__(self):
        super().__init__()
        self.title('PumpkinScheduler')
        self.geometry('900x700')

        self.rcon_servers = []
        self.setup_gui()
        self.load_config()
        self.connect_all_servers()
        self.start_background_task_execution()

    def setup_gui(self):
        self.servers_frame = ctk.CTkFrame(self)
        self.servers_frame.pack(fill='x', padx=10, pady=10)

        self.server_entries = []
        for i in range(9):
            frame = ctk.CTkFrame(self.servers_frame)
            frame.pack(fill='x', pady=2)

            address = ctk.CTkEntry(frame, placeholder_text=f"Server {i+1} Address")
            address.pack(side='left', fill='x', expand=True, padx=2)
            port = ctk.CTkEntry(frame, placeholder_text="Port")
            port.pack(side='left', fill='x', expand=True, padx=2)
            password = ctk.CTkEntry(frame, placeholder_text="Password", show="*")
            password.pack(side='left', fill='x', expand=True, padx=2)

            self.server_entries.append((address, port, password))

        self.command_frame = ctk.CTkFrame(self)
        self.command_frame.pack(fill='x', padx=10, pady=10)

        self.command_entry = ctk.CTkEntry(self.command_frame, placeholder_text="Command to schedule")
        self.command_entry.pack(side='left', fill='x', expand=True, padx=2)
        self.cron_entry = ctk.CTkEntry(self.command_frame, placeholder_text="Cron Expression (e.g., '* * * * *')")
        self.cron_entry.pack(side='left', fill='x', expand=True, padx=2)

        self.schedule_button = ctk.CTkButton(self.command_frame, text="Schedule Command", command=lambda: self.schedule_command(self.command_entry.get(), self.cron_entry.get()))
        self.schedule_button.pack(side='left', padx=10)

        self.scheduled_commands_listbox = tk.Listbox(self)
        self.scheduled_commands_listbox.pack(padx=10, pady=10, fill='both', expand=True)

    def connect_all_servers(self):
        self.rcon_servers.clear()
        for address, port, password in self.server_entries:
            address_value, port_value, password_value = address.get(), port.get(), password.get()
            if address_value and port_value and password_value:
                server = RCONServer(address_value, port_value, password_value)
                server.connect()
                if server.connected:
                    self.rcon_servers.append(server)
            else:
                print("Missing server details. Auto-connect skipped for an incomplete entry.")

    def schedule_command(self, command, cron_expression):
        if command and cron_expression:
            next_run = croniter(cron_expression, datetime.datetime.utcnow()).get_next(datetime.datetime)
            self.scheduled_commands_listbox.insert(tk.END, f"{command} - {cron_expression} - Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Scheduled command '{command}' for next run at {next_run} UTC")

    def start_background_task_execution(self):
        def task_execution():
            while True:
                now = datetime.datetime.utcnow()
                for i in range(self.scheduled_commands_listbox.size()):
                    item = self.scheduled_commands_listbox.get(i)
                    command, cron_expression, _ = item.rsplit(" - ", 2)
                    next_run_str = _.replace("Next run: ", "")
                    next_run = datetime.datetime.strptime(next_run_str, '%Y-%m-%d %H:%M:%S')
                    if now >= next_run:
                        for server in self.rcon_servers:
                            if server.connected:
                                server.disconnect()  # Disconnect before sending a new command
                                server.reconnect()  # Reconnect
                                try:
                                    response = server.rcon_client.command(command)
                                    print(f"Executed command: {command} on {server.address}. Response: {response}")
                                except Exception as e:
                                    print(f"Error executing command on {server.address}: {e}")
                                    server.reconnect()
                        next_run = croniter(cron_expression, now).get_next(datetime.datetime)
                        self.scheduled_commands_listbox.delete(i)
                        self.scheduled_commands_listbox.insert(i, f"{command} - {cron_expression} - Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(60)

        threading.Thread(target=task_execution, daemon=True).start()

    def load_config(self):
        try:
            with open(self.CONFIG_FILE, "r") as file:
                data = json.load(file)
                servers = data.get("servers", [])
                for i, server in enumerate(servers):
                    if i < len(self.server_entries):
                        self.server_entries[i][0].insert(0, server["address"])
                        self.server_entries[i][1].insert(0, server["port"])
                        self.server_entries[i][2].insert(0, server["password"])
                commands = data.get("scheduled_commands", [])
                for command in commands:
                    self.schedule_command(command["command"], command["cron_expression"])
            print("Configuration and scheduled commands loaded successfully.")
        except FileNotFoundError:
            print("Configuration file not found.")
        except Exception as e:
            print(f"Error loading configuration: {e}")

    def on_close(self):
        self.save_config()
        self.destroy()

    def save_config(self):
        config_data = {
            "servers": [
                {"address": entry[0].get(), "port": entry[1].get(), "password": entry[2].get()}
                for entry in self.server_entries
            ],
            "scheduled_commands": [
                {"command": item.split(" - ")[0], "cron_expression": item.split(" - ")[1]}
                for item in self.scheduled_commands_listbox.get(0, tk.END)
            ]
        }
        try:
            with open(self.CONFIG_FILE, "w") as file:
                json.dump(config_data, file, indent=4)
            print("Configuration and scheduled commands saved successfully.")
        except Exception as e:
            print(f"Error saving configuration: {e}")

if __name__ == "__main__":
    app = RCONScheduler()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
