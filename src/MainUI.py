from Globalvar import Globalvar
import tkinter as tk
from tkinter import ttk
from tktooltip import ToolTip
import threading
import sys
from datetime import datetime

from config import USERNAME_1, USERNAME_2, USERNAME_3, USERNAMES

# Constants for action types
ACTION_FROM_TEXT = 'from-text'
ACTION_TO_TEXT = 'to-text'
ACTION_FULL = 'full'
ACTION_UPDATE = 'update'
ACTION_UPDATE_ALL = 'update-all'

HEADLESS = 'headless'

# Global main variable
main = None
glv = Globalvar()

# Dictionary to store buttons and tabs
buttons = {}
log_tabs = {}
force_var = None
headless_var = None
radio_var = None


class LogTab(ttk.Frame):
    def __init__(self, parent, action_name, username):
        super().__init__(parent)
        self.action_name = action_name
        self.username = username
        self.glv = Globalvar.get_instance(action_name, username)
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


def run_thread_manager(action, ids, selected_username, headless=False):
    """Runs the ThreadManager in a separate thread."""
    from ThreadManager import ThreadManager as MainApp
    global main

    # Get the specific Globalvar instance for this action-username combination
    glv_instance = Globalvar.get_instance(action, selected_username)

    main = MainApp(glv_instance)
    main.glv.force = force_var.get() if force_var is not None else False

    if not headless:
        headless = headless_var.get() if headless_var is not None else False

    if action == ACTION_FROM_TEXT:
        main.glv.create_thread = False
        main.glv.from_text = True
    elif action == ACTION_TO_TEXT:
        main.glv.create_thread = True
        main.glv.only_text = True
    elif action == ACTION_FULL:
        main.glv.create_thread = True
        main.glv.only_text = False
    elif action == ACTION_UPDATE:
        main.glv.update = True
    elif action == ACTION_UPDATE_ALL:
        main.glv.update_all = True
        main.glv.update = True

    main.glv.selected_username = selected_username
    glv_instance.start_driver(headless)
    main.start(ids)


def button_click(action):
    """Handles button click events."""
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
        if not notebook.winfo_viewable():
            notebook.grid()

        # Set up the log callback for this specific instance
        glv_instance = Globalvar.get_instance(action, selected_username)
        glv_instance.set_log_callback(lambda msg: new_tab.add_log(msg))

    # Switch to this action's tab
    notebook.select(notebook.index(log_tabs[tab_id]))

    # Reset all buttons to default style
    for btn in buttons.values():
        btn.configure(style='TButton')

    # Set clicked button to green
    buttons[action].configure(style='Green.TButton')

    # Process IDs
    ids = None
    if action in [ACTION_TO_TEXT, ACTION_FULL, ACTION_UPDATE]:
        if '+' in entry_ids_entry.get():
            start_id = int(entry_ids_entry.get()[:-1])
            ids = list(range(start_id, 100 + start_id))
        else:
            ids = entry_ids_entry.get().split(',')
    elif action == ACTION_UPDATE_ALL:
        start_id = int(entry_ids_entry.get().split(',')[0])
        ids = list(range(start_id, 100 + start_id))

    if ids == ['']:
        ids = None

    # Start the ThreadManager in a separate thread
    thread = threading.Thread(target=run_thread_manager, args=(action, ids, selected_username))
    thread.start()


def create_entry_context_menu(event):
    """Creates a context menu for the entry widget."""
    context_menu = tk.Menu(window, tearoff=0)
    context_menu.add_command(label="Cut", command=lambda: event.widget.event_generate("<<Cut>>"))
    context_menu.add_command(label="Copy", command=lambda: event.widget.event_generate("<<Copy>>"))
    context_menu.add_command(label="Paste", command=lambda: event.widget.event_generate("<<Paste>>"))
    context_menu.tk_popup(event.x_root, event.y_root)


def handle_command_line_args():
    if len(sys.argv) > 1:
        action = sys.argv[1]

        if action in [ACTION_FROM_TEXT, ACTION_TO_TEXT, ACTION_FULL, ACTION_UPDATE, ACTION_UPDATE_ALL]:
            selected_username = USERNAME_1
            ids = None

            if len(sys.argv) > 2:
                if sys.argv[2] in USERNAMES:
                    selected_username = sys.argv[2]
                    if len(sys.argv) > 3:
                        ids = sys.argv[3]
                else:
                    ids = sys.argv[2]

            headless = False
            if len(sys.argv) > 4:
                if sys.argv[4] == HEADLESS:
                    headless = True

            if ids:
                if '+' in ids:
                    start_id = int(ids[:-1])
                    ids = list(range(start_id, 100 + start_id))
                else:
                    ids = ids.split(',')

            run_thread_manager(action, ids, selected_username, headless)
            return True
    return False


if __name__ == "__main__":
    if not handle_command_line_args():
        window = tk.Tk()

        # window.iconphoto(True, icon)
        window.title("Thread Handler")

        # Create buttons
        button_frame = ttk.Frame(window)
        button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")

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

        radio_var = tk.StringVar(value=USERNAME_1)
        ttk.Radiobutton(options_frame, text=USERNAME_1, variable=radio_var,
                        value=USERNAME_1).grid(row=0, column=0, padx=5)
        ttk.Radiobutton(options_frame, text=USERNAME_2, variable=radio_var,
                        value=USERNAME_2).grid(row=0, column=1, padx=5)

        ToolTip(options_frame, "Select the account to use")

        headless_var = tk.BooleanVar()
        headless_checkbox = ttk.Checkbutton(options_frame, text="Headless", variable=headless_var)
        headless_checkbox.grid(row=0, column=3, padx=5)

        force_var = tk.BooleanVar()
        force_checkbox = ttk.Checkbutton(options_frame, text="Force", variable=force_var)
        force_checkbox.grid(row=0, column=4, padx=5)

        # Create entry for entry_ids and Log button
        entry_frame = ttk.Frame(window)
        entry_frame.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        entry_ids_label = ttk.Label(entry_frame, text="Entry IDs:")
        entry_ids_label.grid(row=0, column=0, padx=5)

        entry_ids_entry = ttk.Entry(entry_frame, width=39)
        entry_ids_entry.grid(row=0, column=1, padx=5, sticky="ew")
        entry_frame.grid_columnconfigure(1, weight=1)
        entry_ids_entry.bind("<Button-3>", create_entry_context_menu)

        # Create notebook for log tabs (initially hidden)
        notebook = ttk.Notebook(window)
        notebook.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        notebook.grid_remove()  # Initially hidden

        # Create main log panel
        log_frame = ttk.Frame(window)
        log_frame.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        log_frame.grid_remove()  # Initially hidden

        log_text = tk.Text(log_frame, wrap=tk.WORD, width=20, height=10, bg="black", fg="white")
        log_text.pack(expand=True, fill=tk.BOTH)
        log_text.config(state=tk.DISABLED)

        # Configure row and column weights
        window.grid_rowconfigure(3, weight=1)  # Give weight to notebook
        window.grid_rowconfigure(4, weight=0)  # No weight to main log
        window.grid_columnconfigure(0, weight=1)

        # Start the main event loop
        window.mainloop()
