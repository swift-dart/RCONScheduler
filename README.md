RCONScheduler: Game Server Command Scheduler 🕹️

RCONScheduler is a Python-based graphical application designed to schedule and automatically execute commands on multiple Palworld servers using the RCON protocol. This tool is perfect for server administrators who need to automate routine tasks such as saves, broadcasting messages, or restarting servers at specific intervals.

Features 🌟

Multi-Server Management: Configure and manage multiple servers from a single interface.
Command Scheduling: Leverage cron expressions to schedule commands for somewhat precise execution times.
Background Task Execution: Ensures that scheduled tasks run in the background, executing commands at their specified times without manual intervention.
GUI-Based Configuration: Offers a user-friendly graphical interface for adding server details, scheduling commands, and viewing upcoming tasks.
Persistent Configuration: Saves server configurations and scheduled commands to a JSON file for easy management and persistence across sessions.
Auto-Reconnect: Automatically attempts to reconnect to servers if the connection is lost during command execution.

Key Components 🛠️

RCONServer class: Manages RCON connections to Minecraft servers, including connecting, disconnecting, and reconnecting as necessary.
RCONScheduler class (inherits from customtkinter.CTk): The main application window responsible for setting up the GUI, loading/saving configurations, managing server connections, and scheduling/executing commands.

How It Works 🔧

Server Configuration: Enter details for multiple servers, including address, port, and password.
Command Scheduling: Specify commands to execute and their timing using cron syntax.
Execution Loop: A background thread continuously checks the schedule and executes commands on configured servers at the right times.

Dependencies 📦

customtkinter: For modern GUI components.
mcrcon: To manage RCON communication with Minecraft servers(Works with Palworld so I used it).
croniter: For parsing cron expressions and calculating next execution times.
tkinter: Python's standard GUI library, used alongside customtkinter for the application interface.
threading: To run the command execution loop in the background.
json: For loading and saving application configurations.

Usage 🚀

Double click the exe it will open the program. Close the program and open it again and a json file will have been created , and then the GUI will guide you through configuring your servers and scheduling commands. If opening the py file itself not the exe make sure all the dependencies are installed!.

Note 📝

This application is designed for flexibility, allowing for easy expansion or modification to meet specific administrative needs. Whether managing a single server or a fleet, RCONScheduler aims to simplify your tasks through automation.

