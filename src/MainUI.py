from Globalvar import Globalvar
import tkinter as tk
from tkinter import ttk
from tktooltip import ToolTip
import threading
import sys
from datetime import datetime

# Assuming USERNAME_1, USERNAME_2, USERNAME_3, USERNAMES are correctly defined in config.py
from config import USERNAME_1, USERNAME_2, USERNAME_3, USERNAMES  # Ensure these match your config

# Constants for action types
ACTION_FROM_TEXT = 'from-text'
ACTION_TO_TEXT = 'to-text'
ACTION_FULL = 'full'
ACTION_UPDATE = 'update'
ACTION_UPDATE_ALL = 'update-all'

HEADLESS = 'headless'

# Global main variable
main = None  # This is for the ThreadManager instance
glv = Globalvar()  # This is the initial Globalvar instance, though LogTab and run_thread_manager get specific ones

# --- Module-level variables for UI elements and state ---
# These are initialized as None and will be assigned Tkinter objects/variables
# inside start_ui_and_app if the UI is created.
buttons = {}
log_tabs = {}
force_var = None
headless_var = None
radio_var = None
notebook = None
entry_ids_entry = None
window = None


# No need for log_text and log_frame at module level unless used by callbacks outside setup

class LogTab(ttk.Frame):
    def __init__(self, parent, action_name, username):
        super().__init__(parent)
        self.action_name = action_name
        self.username = username
        # Each LogTab gets its own specific Globalvar instance
        self.glv_instance = Globalvar.get_instance(action_name, username)
        self.log_text = None
        self.setup_ui()

    def setup_ui(self):
        # Create main layout
        self.log_text = tk.Text(self, wrap=tk.WORD, height=10, width=90, bg="black", fg="white")
        self.log_text.pack(expand=True, fill=tk.BOTH)
        self.log_text.config(state=tk.DISABLED)

    def add_log(self, message):
        """Add a new log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, formatted_message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)


def run_thread_manager(action, ids, selected_username,
                       headless_arg=False):  # Renamed headless to headless_arg to avoid conflict
    """Runs the ThreadManager in a separate thread."""
    from ThreadManager import ThreadManager as MainApp
    global main, force_var, headless_var  # Access module-level Tkinter Vars

    # Get the specific Globalvar instance for this action-username combination
    glv_instance = Globalvar.get_instance(action, selected_username)

    current_main = MainApp(glv_instance)  # Use a local var for this specific thread's MainApp

    # Get values from Tkinter variables if they exist (UI mode)
    # Otherwise, force_var.get() would fail if UI wasn't initialized
    if force_var:
        current_main.glv.force = force_var.get()
    else:
        current_main.glv.force = False  # Default if UI not up (e.g. CLI mode)

    effective_headless = headless_arg  # Use passed argument first
    if not effective_headless and headless_var:  # If not forced by arg, check UI var
        effective_headless = headless_var.get()

    if action == ACTION_FROM_TEXT:
        current_main.glv.create_thread = False
        current_main.glv.from_text = True
    elif action == ACTION_TO_TEXT:
        current_main.glv.create_thread = True
        current_main.glv.only_text = True
    elif action == ACTION_FULL:
        current_main.glv.create_thread = True
        current_main.glv.only_text = False
    elif action == ACTION_UPDATE:
        current_main.glv.update = True
    elif action == ACTION_UPDATE_ALL:
        current_main.glv.update_all = True
        current_main.glv.update = True

    current_main.glv.selected_username = selected_username
    glv_instance.start_driver(effective_headless)  # Use the determined headless state
    current_main.start(ids)

    # Assign to global 'main' if you need to access the *last* started manager from elsewhere
    # Be cautious with this if multiple threads can run; 'main' will only point to the latest.
    main = current_main


def button_click(action):
    """Handles button click events."""
    # These globals are read here, so they must be assigned correctly in start_ui_and_app
    global radio_var, entry_ids_entry, notebook, log_tabs, buttons

    if radio_var is None or entry_ids_entry is None or notebook is None:
        print("Error: UI elements not initialized before button click!")
        return

    selected_username = radio_var.get()

    # Create unique tab identifier
    tab_id = f"{action}_{selected_username}"
    tab_title = f"{action.replace('-', ' ').title()} - {selected_username}"

    # Create new tab for this action and username combination if it doesn't exist
    if tab_id not in log_tabs:
        new_tab = LogTab(notebook, action, selected_username)
        log_tabs[tab_id] = new_tab
        notebook.add(new_tab, text=tab_title)

        # Show notebook if it was hidden
        if not notebook.winfo_viewable():  # Checks if the widget is mapped (visible)
            notebook.grid()  # This might re-add it if it was grid_removed. Consider pack or place if that's the original.

        # Set up the log callback for this specific instance
        glv_instance = Globalvar.get_instance(action, selected_username)
        glv_instance.set_log_callback(lambda msg: new_tab.add_log(msg))

    # Switch to this action's tab
    notebook.select(notebook.index(log_tabs[tab_id]))

    # Reset all buttons to default style
    for btn_widget in buttons.values():  # Iterate over widget objects
        if isinstance(btn_widget, ttk.Button):  # Ensure it's a button
            btn_widget.configure(style='TButton')

    # Set clicked button to green
    if action in buttons and isinstance(buttons[action], ttk.Button):
        # Ensure a 'Green.TButton' style is defined, e.g., in start_ui_and_app
        # style = ttk.Style()
        # style.configure('Green.TButton', background='green', foreground='white') # Example
        buttons[action].configure(style='Green.TButton')

    # Process IDs
    ids_str = entry_ids_entry.get()
    ids = None
    if action in [ACTION_TO_TEXT, ACTION_FULL, ACTION_UPDATE]:
        if '+' in ids_str:
            try:
                start_id = int(ids_str[:-1])
                ids = list(range(start_id, 100 + start_id))
            except ValueError:
                print(f"Invalid start ID format: {ids_str}")
                ids = None  # Or handle error appropriately
        elif ids_str.strip():  # Ensure not empty string
            ids = ids_str.split(',')
    elif action == ACTION_UPDATE_ALL:
        if ids_str.strip():
            try:
                start_id = int(ids_str.split(',')[0])  # Take first ID if multiple are given for some reason
                ids = list(range(start_id, 100 + start_id))
            except (ValueError, IndexError):
                print(f"Invalid start ID for Update All: {ids_str}")
                ids = None

    if ids == [''] or ids == []:  # Check for empty list from split or explicit empty string
        ids = None

    # Start the ThreadManager in a separate thread
    # Pass False for headless by default from UI click, run_thread_manager will check UI var
    thread = threading.Thread(target=run_thread_manager, args=(action, ids, selected_username, False))
    thread.start()


def create_entry_context_menu(event):
    """Creates a context menu for the entry widget."""
    # 'window' needs to be the tk.Tk() instance.
    # If event.widget.master is not the main window, this might not be ideal.
    # Using event.widget.winfo_toplevel() is usually safer for the parent of a context menu.
    parent_widget = event.widget.winfo_toplevel()
    context_menu = tk.Menu(parent_widget, tearoff=0)
    context_menu.add_command(label="Cut", command=lambda: event.widget.event_generate("<<Cut>>"))
    context_menu.add_command(label="Copy", command=lambda: event.widget.event_generate("<<Copy>>"))
    context_menu.add_command(label="Paste", command=lambda: event.widget.event_generate("<<Paste>>"))
    context_menu.tk_popup(event.x_root, event.y_root)


def handle_command_line_args():
    # No changes needed here if it correctly calls run_thread_manager with headless=True/False
    if len(sys.argv) > 1:
        action = sys.argv[1]

        if action in [ACTION_FROM_TEXT, ACTION_TO_TEXT, ACTION_FULL, ACTION_UPDATE, ACTION_UPDATE_ALL]:
            selected_username = USERNAME_1  # Default username
            ids = None

            cli_arg_offset = 0
            if len(sys.argv) > 2:
                if sys.argv[2] in USERNAMES:
                    selected_username = sys.argv[2]
                    cli_arg_offset = 1  # Username was present
                    if len(sys.argv) > 3:
                        ids_str_cli = sys.argv[3]
                else:
                    ids_str_cli = sys.argv[2]
            else:  # Only action provided
                ids_str_cli = None

            # Determine headless based on argument after IDs (or username if IDs absent)
            headless_cli = False
            ids_arg_index = 2 + cli_arg_offset  # Index where headless flag might be if IDs were present
            username_arg_index = 2  # Index where headless flag might be if only username (no IDs) was present

            potential_headless_arg_index = 3 + cli_arg_offset  # if IDs are present
            if ids_str_cli is None and len(sys.argv) > (2 + cli_arg_offset):  # No IDs, check arg after username
                potential_headless_arg_index = 2 + cli_arg_offset + 1

            if len(sys.argv) > potential_headless_arg_index - 1 and sys.argv[
                potential_headless_arg_index - 1] == HEADLESS:
                headless_cli = True
            elif ids_str_cli and len(sys.argv) > (3 + cli_arg_offset) and sys.argv[
                3 + cli_arg_offset] == HEADLESS:  # if ID was at 3, headless at 4
                headless_cli = True

            processed_ids = None
            if ids_str_cli:
                if '+' in ids_str_cli:
                    try:
                        start_id = int(ids_str_cli[:-1])
                        processed_ids = list(range(start_id, 100 + start_id))
                    except ValueError:
                        print(f"Invalid CLI ID format with '+': {ids_str_cli}")
                else:
                    processed_ids = ids_str_cli.split(',')
                    if processed_ids == ['']: processed_ids = None

            print(f"CLI: action={action}, ids={processed_ids}, user={selected_username}, headless={headless_cli}")
            run_thread_manager(action, processed_ids, selected_username, headless_cli)  # Pass headless_cli
            return True
    return False


def start_ui_and_app():
    """Initializes and starts the UI or command-line process."""
    # Crucial: Declare all module-level variables that will be assigned Tkinter objects
    # or Tkinter control variables as global here.
    global window, buttons, radio_var, headless_var, force_var, entry_ids_entry, notebook, log_tabs

    if not handle_command_line_args():
        window = tk.Tk()  # Assigns to module-level 'window'

        # Define custom style for green button if not already defined
        style = ttk.Style(window)  # Pass window to Style constructor
        style.configure('Green.TButton', background='green', foreground='black')  # Example, adjust colors

        window.title("Thread Handler")

        # Create buttons
        button_frame = ttk.Frame(window)
        button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # 'buttons' is already global, so this modifies the module-level dict
        buttons[ACTION_FROM_TEXT] = ttk.Button(button_frame, text="From Text",
                                               command=lambda: button_click(ACTION_FROM_TEXT))
        buttons[ACTION_FROM_TEXT].grid(row=0, column=0, padx=5)
        ToolTip(buttons[ACTION_FROM_TEXT], "Make thread from text file")

        buttons[ACTION_TO_TEXT] = ttk.Button(button_frame, text="To Text", command=lambda: button_click(ACTION_TO_TEXT))
        buttons[ACTION_TO_TEXT].grid(row=0, column=1, padx=5)
        ToolTip(buttons[ACTION_TO_TEXT], "Only make a text file")

        buttons[ACTION_FULL] = ttk.Button(button_frame, text="Full", command=lambda: button_click(ACTION_FULL))
        buttons[ACTION_FULL].grid(row=0, column=2, padx=5)
        ToolTip(buttons[ACTION_FULL], "Make and post thread")

        buttons[ACTION_UPDATE] = ttk.Button(button_frame, text="Update", command=lambda: button_click(ACTION_UPDATE))
        buttons[ACTION_UPDATE].grid(row=0, column=3, padx=5)
        ToolTip(buttons[ACTION_UPDATE], "Update entry links and its thread.")

        buttons[ACTION_UPDATE_ALL] = ttk.Button(button_frame, text="Update All",
                                                command=lambda: button_click(ACTION_UPDATE_ALL))
        buttons[ACTION_UPDATE_ALL].grid(row=0, column=4, padx=5)
        ToolTip(buttons[ACTION_UPDATE_ALL],
                "Update entry links and its thread.\nFor 100 entries starting at the given one.")

        # Create radio buttons and checkboxes
        options_frame = ttk.Frame(window)
        options_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Assignments to radio_var, headless_var, force_var update the module-level ones
        radio_var = tk.StringVar(value=USERNAME_1)
        ttk.Radiobutton(options_frame, text=USERNAME_1, variable=radio_var,
                        value=USERNAME_1).grid(row=0, column=0, padx=5)
        ttk.Radiobutton(options_frame, text=USERNAME_2, variable=radio_var,
                        value=USERNAME_2).grid(row=0, column=1, padx=5)
        # Add USERNAME_3 if it's part of USERNAMES and intended for UI
        if USERNAME_3 in USERNAMES:
            ttk.Radiobutton(options_frame, text=USERNAME_3, variable=radio_var,
                            value=USERNAME_3).grid(row=0, column=2, padx=5)

        ToolTip(options_frame, "Select the account to use")

        headless_var = tk.BooleanVar()
        # Adjust column based on how many radio buttons there are
        headless_col = 2 if USERNAME_3 not in USERNAMES else 3
        headless_checkbox = ttk.Checkbutton(options_frame, text="Headless", variable=headless_var)
        headless_checkbox.grid(row=0, column=headless_col, padx=5)
        ToolTip(headless_checkbox, "Run browser in headless mode (no UI).")

        force_var = tk.BooleanVar()
        force_checkbox = ttk.Checkbutton(options_frame, text="Force", variable=force_var)
        force_checkbox.grid(row=0, column=headless_col + 1, padx=5)
        ToolTip(force_checkbox, "Force operation even if conditions normally prevent it.")

        # Create entry for entry_ids
        entry_frame = ttk.Frame(window)
        entry_frame.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        entry_ids_label = ttk.Label(entry_frame, text="Entry IDs:")
        entry_ids_label.grid(row=0, column=0, padx=5)

        entry_ids_entry = ttk.Entry(entry_frame, width=39)  # Assigns to module-level
        entry_ids_entry.grid(row=0, column=1, padx=5, sticky="ew")
        entry_frame.grid_columnconfigure(1, weight=1)
        entry_ids_entry.bind("<Button-3>", create_entry_context_menu)

        # Create notebook for log tabs (initially hidden)
        notebook = ttk.Notebook(window)  # Assigns to module-level
        # 'log_tabs' is already global (dict), it's modified in button_click
        notebook.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        notebook.grid_remove()  # Initially hidden

        # Configure row and column weights
        window.grid_rowconfigure(3, weight=1)  # Give weight to notebook
        window.grid_columnconfigure(0, weight=1)

        # Remove the unused main log panel at the bottom to simplify layout unless needed
        # log_frame = ttk.Frame(window)
        # log_frame.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        # log_frame.grid_remove()
        # log_text_main = tk.Text(log_frame, wrap=tk.WORD, width=20, height=10, bg="black", fg="white")
        # log_text_main.pack(expand=True, fill=tk.BOTH)
        # log_text_main.config(state=tk.DISABLED)
        # window.grid_rowconfigure(4, weight=0)

        window.mainloop()


if __name__ == "__main__":
    start_ui_and_app()