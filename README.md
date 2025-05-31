```markdown
# Anime-Sharing Thread Manager

This project is a Python-based application designed to automate the creation, posting, and management of threads on the Anime-Sharing forum. It streamlines content gathering from Hcapital, handles image uploads to various hosting services, manages download links, and provides both a Graphical User Interface (GUI) and a Command-Line Interface (CLI) for operation.

## Features

*   **Automated Thread Operations:**
    *   Create new threads from scratch.
    *   Generate thread content as text files for review before posting.
    *   Update existing threads with new links or image information.
    *   Batch processing of multiple entries.
*   **Multi-Account Support:** Manage and post threads using different Anime-Sharing user accounts (e.g., `user1`, `user2`, `user3`).
*   **Data Integration:**
    *   Fetches entry data (titles, descriptions, release dates, developer info, images, links) from a Hcapital instance.
*   **Image Hosting:**
    *   Uploads images to services like ImgBB, TurboImageHost, and IwantTF.
*   **Link Management:**
    *   Handles download links from various file hosting services (e.g., Rapidgator, Mexashare, Katfile).
    *   Can automatically attempt to re-upload files to ensure link consistency across hosts.
*   **Templating System:**
    *   Uses customizable templates (per user) to format thread subjects, bodies, and tags.
*   **User Interfaces:**
    *   **GUI (Tkinter):** An interactive window for managing operations, selecting users, setting options, and viewing logs per action.
    *   **CLI:** Allows for scripted and automated execution of tasks.
*   **Logging:** Provides real-time logging in the GUI for each initiated action and also logs errors to a `log.txt` file.
*   **Configuration:**
    *   Usernames and site-specific constants are managed in `src/config.py`.
    *   Sensitive credentials (accounts for Anime-Sharing, file hosts, image hosts, database) are managed via an `.env` file.

## Prerequisites

*   Python 3.8+
*   pip (Python package installer)
*   A compatible web browser (Chrome or Firefox)
*   WebDriver:
    *   **Chrome:** `chromedriver_autoinstaller` is used, which should handle this automatically.
    *   **Firefox:** Geckodriver needs to be downloaded and placed in a location accessible by the script (e.g., `~/bin/geckodriver` as per default configuration in `DriverProxy.py`).
*   MySQL server (optional, if not using the `MockDB` or for specific user configurations).
*   Access to a Hcapital instance (either local or remote, configured in `Globalvar.py`).

## Setup

1.  **Clone the Repository or Download Files:**
    Obtain all project files and place them in a directory on your system. The project structure is assumed to be:
    ```
    YourProjectDirectory/
    │   ├── templates/
    │   │   └── username
    │   │   └── ... (other user templates)
    │   ├── images/
    │   │   └── icon.ico
    │   │   └── ... (other images)
    ├── src/
    │   ├── hosts/
    │   │   └── Host.py
    │   │   └── Rapidgator.py
    │   │   └── Mexashare.py
    │   │   └── ... (other host modules)
    │   ├── MainUI.py
    │   ├── Globalvar.py
    │   ├── ... (other .py files)
    │   ├── includes/
    │   │   └── jquery.js
    │   ├── config.py
    │   └── newId             # File to store the next entry ID
    │   └── fixId             # File used by update_all logic
    │   └── log.txt           # Log file
    ├── .env                  # (You will create this)
    └── README.md
    ```

2.  **Adjust `Globalvar.py` (Important Path Configuration):**
    Open `src/Globalvar.py` and locate the `__init__` method. The `self.path` variable is critical and might be hardcoded.
    ```python
    # Inside Globalvar.__init__
    self.home = os.path.expanduser("~")
    if 'root' in self.home or '{pc_user}' in self.home: # Original developer's condition
        self.path = f'{self.home}/Git/CreateThread/source'
        self.includes_path =  f'{self.home}/Git/CreateThread/source/includes'
    else: # Another user's condition
        self.path = f'{self.home}/Threads_{username}/Create/'
        # self.includes_path might need to be set here too if different
        self.includes_path = os.path.join(self.path, 'includes') # Example adjustment

    # You may need to change self.path and self.includes_path
    # to point to your actual 'src' directory (or its equivalent).
    # For example, if your project is in C:\MyTool and src is C:\MyTool\src:
    # self.path = 'C:\\MyTool\\src'
    # self.includes_path = 'C:\\MyTool\\src\\includes'
    # Or using relative paths (ensure Python's working directory is correct):
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # self.path = script_dir
    # self.includes_path = os.path.join(self.path, 'includes')
    ```
    This path determines where the script looks for `newId`, `templates/`, `includes/`, and `log.txt`.

3.  **Install Dependencies:**
    Navigate to your project directory in the terminal and install the required Python packages:
    ```bash
    pip install selenium tk tktooltip Pillow pymysql python-dotenv chromedriver-autoinstaller requests
    ```
    (Note: `Pillow` for image handling, `requests` for `MockDB`).

4.  **Create and Configure `.env` File:**
    In the root of `YourProjectDirectory/` (i.e., at the same level as the `src/` folder), create a file named `.env`. Populate it with your credentials. Refer to `src/Accounts.py` for the expected environment variable names.
    **Example `.env` structure:**
    ```dotenv
    # Anime-Sharing Accounts (Index-based, e.g., _0_, _1_)
    # ANIME_SHARING_3_... is often used for USERNAME_{USERNAME}}
    ANIME_SHARING_0_USERNAME=your_as_username_1
    ANIME_SHARING_0_PASSWORD=your_as_password_1
    ANIME_SHARING_1_USERNAME=your_as_username_2
    ANIME_SHARING_1_PASSWORD=your_as_password_2
    ANIME_SHARING_3_USERNAME={username}_username # Corresponds to USERNAME_{USERNAME}
    ANIME_SHARING_3_PASSWORD={username}_password

    # Hcapital/Local Database (for MySQL)
    LOCALHOST_0_HOST=your_db_host
    LOCALHOST_0_USERNAME=your_db_user
    LOCALHOST_0_PASSWORD=your_db_password
    LOCALHOST_0_DATABASE=your_db_name

    # File Host Accounts (Index-based if multiple accounts per host)
    RAPIDGATOR_0_USERNAME=your_rg_user
    RAPIDGATOR_0_PASSWORD=your_rg_pass

    MEXASHARE_0_USERNAME=your_ms_user
    MEXASHARE_0_PASSWORD=your_ms_pass

    KATFILE_0_USERNAME=your_kf_user
    KATFILE_0_PASSWORD=your_kf_pass
    # KATFILE_0_API=your_kf_api_key # If API key is used and configured

    # Image Host Accounts (if login is required)
    IWTF_0_USERNAME=your_iwanttf_user
    IWTF_0_PASSWORD=your_iwanttf_pass

    TURBO_IMAGE_0_USERNAME=your_turboimage_user
    TURBO_IMAGE_0_EMAIL=your_turboimage_email
    TURBO_IMAGE_0_PASSWORD=your_turboimage_pass

    # Add other services (FICHIER, DDOWNLOAD, ROSEFILE, FIKPER, FILE, SABERCAT) as needed
    ```

5.  **Database Setup (MySQL - Optional):**
    *   If you intend to use the MySQL database backend (`DB.py`):
        *   Ensure your MySQL server is running.
        *   Create the database specified in your `.env` file (`LOCALHOST_0_DATABASE`).
        *   Create the required tables (`entries`, `threads`). The schema is not fully defined here but can be inferred from `DB.py` and related modules.
    *   The application can also use `MockDB.py` which makes calls to `hcapital.tk` instead of a local DB, particularly for the `USERNAME_{USERNAME}` or if `self.path` in `Globalvar.py` is not the primary developer's path.

6.  **Hcapital Instance:**
    Ensure the Hcapital instance (defined by `self.glv.get_root()` in `Hcapital.py`, which can be `http://localhost` or `http://www.hcapital.tk`) is accessible and provides the necessary data.

7.  **Templates:**
    Place your thread templates in the `src/templates/` directory. Template files should be named after the Anime-Sharing usernames defined in `src/config.py` (e.g., `user1`, `user2`). These templates use placeholders like `#cover#`, `#title_kanji#`, `#links#`, etc., which are filled by `FillTemplate.py`.

8.  **Initial ID:**
    The `src/newId` file stores the starting entry ID for processing. Ensure it exists and contains a valid number.

## Usage

### GUI (Graphical User Interface)

To run the application with its GUI:
```bash
python src/MainUI.py
```
This will open the "Thread Handler" window.

**GUI Components:**

*   **Action Buttons:**
    *   `From Text`: Create thread content from existing local text files (Not fully detailed in provided code but action exists).
    *   `To Text`: Generate thread content (subject, body, tags) and save it to a `.txt` file in `~/Threads_<username>/` without posting.
    *   `Full`: Generate thread content and post it to Anime-Sharing.
    *   `Update`: Update specified entry links and its corresponding thread on Anime-Sharing.
    *   `Update All`: Update links for 100 entries starting from the given ID.
*   **Username Selection:** Radio buttons to select the Anime-Sharing account to use (e.g., `user1`, `user2`, `user3`).
*   **Options:**
    *   `Headless`: Checkbox to run the browser in headless mode (no visible browser window).
    *   `Force`: Checkbox to force certain operations, like re-processing an entry.
*   **Entry IDs:** Input field to specify entry IDs.
    *   Single ID: `12345`
    *   Multiple IDs (comma-separated): `12345,12346,12347`
    *   Range (for `Update All` or `Full` with multiple IDs): `12345+` (processes 100 entries starting from 12345).
*   **Log Tabs:** Below the controls, a tabbed area will appear. Each action initiated for a specific user will create a new tab showing real-time log messages for that operation.

### CLI (Command-Line Interface)

The application can also be run from the command line:
```bash
python src/MainUI.py <action> [username] [ids] [headless]
```

**Arguments:**

*   `<action>`: (Required) One of `from-text`, `to-text`, `full`, `update`, `update-all`.
*   `[username]`: (Optional) Username to use (e.g., `user1`, `user2`, `user2`). Defaults to `user1` if not specified or if the argument is not a valid username but is instead `ids`.
*   `[ids]`: (Optional) Entry ID(s). Comma-separated or `ID+` for a range.
*   `[headless]`: (Optional) Pass the string `headless` to run in headless mode.

**CLI Examples:**

*   Post a full thread for entry `12345` using `user1` account:
    ```bash
    python src/MainUI.py full user1 12345
    ```
*   Update 100 entries starting from ID `1000` using `{username}` account in headless mode:
    ```bash
    python src/MainUI.py update-all {username} 1000+ headless
    ```
*   Generate text file for entry `54321` (default user `user1`):
    ```bash
    python src/MainUI.py to-text 54321
    ```

## File Structure Overview

*   `src/`: Contains all Python source code.
    *   `MainUI.py`: Entry point, GUI logic, CLI argument parsing.
    *   `ThreadManager.py`: Core workflow orchestration.
    *   `Globalvar.py`: Global state, WebDriver management, utility functions, path configurations.
    *   `AnimeSharing.py`: Handles interactions with Anime-Sharing forum.
    *   `Hcapital.py`: Handles interactions with the Hcapital data source.
    *   `ImageExtractor.py`, `ImgBB.py`, `TurboImage.py`, `IwantTF.py`: Modules for image handling and uploading.
    *   `FillTemplate.py`, `Links.py`, `Tabs.py`: Logic for creating thread content using templates.
    *   `DB.py`, `MockDB.py`: Database interaction layers.
    *   `Accounts.py`: Loads and provides account credentials from `.env`.
    *   `config.py`: Static application configuration (e.g., usernames).
    *   `DriverProxy.py`: Manages thread-safe Selenium WebDriver instances.
    *   `hosts/`: Modules for specific file hosting services (e.g., `Rapidgator.py`).
    *   `templates/`: Directory containing thread templates (e.g., `user1`, `user2`).
    *   `includes/`: Contains auxiliary files like `jquery.js`.
    *   `newId`, `fixId`: Text files storing current/next entry IDs for processing.
    *   `log.txt`: Main application error log file.
*   `.env`: (User-created) Stores sensitive credentials.
*   `~/Threads_<username>/`: (Created by the app) Default location for storing generated `.txt` thread files when using "To Text" action. Path is relative to the user's home directory.
*   `src/temp/`: (Created by the app, relative to `self.path`) Temporary storage for downloads and images during processing.

## Troubleshooting

*   **Path Issues:** If the application cannot find templates, `newId`, or `jquery.js`, double-check the `self.path` and `self.includes_path` settings in `src/Globalvar.py` and ensure they correctly point to your project's `src` (or equivalent) directory.
*   **WebDriver Errors:**
    *   Ensure you have the correct WebDriver for your browser version installed and accessible. `chromedriver_autoinstaller` should handle Chrome. For Firefox, Geckodriver must be manually set up.
    *   "Driver not initialized for this thread" usually indicates an issue with WebDriver setup or threading.
*   **Login Failures:** Verify credentials in your `.env` file are correct and that the accounts are active on the respective services.
*   **Hcapital Access:** Ensure the Hcapital URL (local or remote) is correct and the service is running and responsive.
*   **Permissions:** The application needs write permissions for `log.txt`, `newId`, `fixId`, the `src/temp/` directory, and `~/Threads_<username>/` directories.

```