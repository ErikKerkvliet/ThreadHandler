import sys
import os
from selenium.common.exceptions import NoSuchElementException  # Ensure this is imported
from selenium.webdriver.common.by import By

from datetime import datetime
import time  # Added import for time.sleep

# Determine the directory of the current script (Globalvar.py)
_current_script_dir = os.path.dirname(os.path.abspath(__file__))

from src.hosts.Host import HOST_NAMES
from src.hosts.Rapidgator import Rapidgator
from src.hosts.Mexashare import Mexashare
from src.hosts.Katfile import Katfile
from Accounts import Accounts
from DB import DB
from Hcapital import Hcapital
from DriverProxy import DriverProxy
import shutil
import logging

import re

from random import uniform
from logging.handlers import RotatingFileHandler

from src.hosts.Host import (
    HOST_NAME_RAPIDGATOR, HOST_NAME_MEXASHARE, HOST_NAME_KATFILE, HOST_NAME_DDOWNLOAD,
)

from config import USERNAMES, USERNAME_3, SITE_SHARING


class Globalvar:
    _instances = {}

    @classmethod
    def get_instance(cls, action, username):
        key = f"{action}_{username}"
        if key not in cls._instances:
            cls._instances[key] = cls()
        return cls._instances[key]

    def __init__(self):
        self.driver = None
        self.log_callback = None
        self.force = False
        self.only_text = False
        self.selected_username = None

        self.only_text = True
        self.create_thread = False  # Create a txt file
        self.from_text = False
        self.previous_error = False
        self.update = False
        self.sharing_nr = ''
        self.update_all = False
        self.log_callback = None
        self.driver = DriverProxy()

        self.home = os.path.expanduser("~")

        self.path = _current_script_dir
        self.includes_path = os.path.join(self.path, 'includes')

        self.logger = self.setup_logger()

        self.downloadPath = None
        self.temp_images_path = None

        self.threads_folder = os.path.join(self.home, 'Threads')

        for username in USERNAMES:
            self.create_folder(os.path.join(self.home, f'Threads_{username}'))

        self.ids = []
        self.id = None
        self.id = self.get_id()
        self.user = None
        # self.selected_username = None # Already initialized above
        # self.force = False # Already initialized above
        self.downloads = {}
        self.romanji_title = ''

        self.hcapital = Hcapital(self)

        self.accounts = Accounts.get_accounts()

        self.project_path = os.path.abspath(os.path.join(_current_script_dir, ".."))
        expected_dev_db_path = os.path.join(self.project_path, 'src')
        if self.path == expected_dev_db_path and (os.getenv('PC_USERNAME') in self.home or 'root' in self.home):
            self.db = DB(self)
        else:
            from MockDB import MockDB
            self.db = MockDB(self)

        self.rapidgator = Rapidgator(self)
        self.mexashare = Mexashare(self, self.get_account(HOST_NAME_MEXASHARE, 0))
        self.katfile = Katfile(self, self.get_account(HOST_NAME_KATFILE, 0))

    def start_driver(self, headless):
        temp_base = os.path.join(self.project_path, 'temp')
        temp = self.create_folder(temp_base)

        user_folder_name = self.selected_username if self.selected_username else "default_user"
        temp_user_path = os.path.join(temp, user_folder_name)
        temp_user = self.create_folder(temp_user_path)

        self.downloadPath = self.create_folder(os.path.join(temp_user, 'downloads'))
        self.temp_images_path = self.create_folder(os.path.join(temp_user, 'images'))

        self.driver.initialize(headless, self.home, self.downloadPath)

    def get_id(self, file='newId'):
        id_file_path = os.path.join(self.path, '..', file)
        entry_id_to_return = getattr(self, 'id', 0)  # Default to existing or 0

        if not hasattr(self, '_id_initialized_from_file') and not self.update:
            try:
                with open(id_file_path, "r") as f:
                    entry_id_str = f.read().strip()

                if ',' in entry_id_str:
                    self.ids = entry_id_str.split(',')
                    entry_id_to_return = int(self.ids[0])
                else:
                    entry_id_to_return = int(entry_id_str)

                # Set self.id here if it's being read for the first time successfully
                self.id = entry_id_to_return
                self._id_initialized_from_file = True
            except FileNotFoundError:
                self.log(f"ID file not found: {id_file_path}. Using default/existing ID: {entry_id_to_return}.",
                         "warning")
            except ValueError:
                self.log(
                    f"Invalid content in ID file: {id_file_path}. Using default/existing ID: {entry_id_to_return}.",
                    "error")

        return self.id  # Always return current self.id

    def set_next_id(self):
        current_id_val = int(getattr(self, 'id', 0))  # Ensure self.id is int before incrementing
        if len(self.ids) > 0:
            del (self.ids[0])
            if len(self.ids) > 0:
                if self.ids[0] == '=':
                    del (self.ids[0])
                    self.write(','.join(self.ids))
                    self.quit()  # Consider if quit is appropriate here
                self.id = int(self.ids[0])
                self.write(','.join(self.ids))
            else:
                self.id = current_id_val + 1
                self.write(str(self.id))
        else:
            self.id = current_id_val + 1
            self.write(str(self.id))
        self._id_initialized_from_file = True

    def write(self, text, file='newId'):
        file_path = os.path.join(self.project_path, file)
        try:
            with open(file_path, "w") as f:
                f.write(str(text))
        except IOError as e:
            self.log(f"Error writing to file {file_path}: {e}", "error")

    def get_hcapital(self, edit=False, web=False):
        extra = ''
        if edit:
            extra = '_'
        return f'{self.get_root(web)}/?v=2&{extra}id='

    def get_root(self, web=False):
        is_dev_condition_met = (os.getenv('PC_USERNAME') in self.home or 'root' in self.home)

        if (is_dev_condition_met or self.update) and not web:
            return 'http://localhost'
        else:
            return 'http://www.hcapital.tk'

    def _retry_find(self, find_func, by, value, wait, max_retries=3):
        for attempt in range(max_retries):
            try:
                return find_func(by, value)
            except NoSuchElementException:
                if attempt < max_retries - 1:
                    time.sleep(wait)
                else:
                    self.log(f"Element not found: '{value}' (by {by}) after {max_retries} retries.", "warning")
                    # For find_element, None is appropriate. For find_elements, it never raises NSEE for "not found".
                    return None
            except Exception as e:
                self.log(f"Error finding element '{value}' (by {by}), attempt {attempt + 1}/{max_retries}: {e}",
                         "error")
                if attempt < max_retries - 1:
                    time.sleep(wait)
                else:
                    if find_func.__name__ == 'find_elements':
                        return []
                    return None
        # Fallback if loop finishes (e.g. max_retries is 0 or negative, though default is 3)
        if find_func.__name__ == 'find_elements':
            return []
        return None

    def get_element(self, by, value, wait=1):
        by = self.un_simplify(by)
        return self._retry_find(self.driver.find_element, by, value, wait)

    def get_elements(self, by, value, wait=1, depth=0, single=False):  # depth is currently unused here
        by = self.un_simplify(by)
        elements = self._retry_find(self.driver.find_elements, by, value, wait)

        # _retry_find for find_elements should return a list (possibly empty if elements are not found or on error after retries)
        if elements is None:  # Should ideally not happen if _retry_find returns [] for find_elements error
            elements = []

        if elements and single:
            return elements[0]
        return elements

    def get_element_in_element(self, parent_element, by, value, single=False):
        original_driver = self.driver
        self.driver = parent_element
        result = self.get_elements(by, value, single=single)
        self.driver = original_driver
        return result

    @staticmethod
    def un_simplify(by):
        # Simplify this: if 'by' is already a By.<TYPE>, return it. Otherwise map.
        if isinstance(by, str):
            if by == 'css':
                return By.CSS_SELECTOR
            elif by == 'tag':
                return By.TAG_NAME
            elif by == 'text' or by == 'link_text':
                return By.LINK_TEXT
            elif by == 'partial_text':
                return By.PARTIAL_LINK_TEXT
            elif by == 'class':
                return By.CLASS_NAME
            # Add other string mappings if necessary, e.g., 'id' -> By.ID, 'name' -> By.NAME
            elif by == 'id':
                return By.ID
            elif by == 'name':
                return By.NAME
            elif by == 'xpath':
                return By.XPATH
            else:
                return by  # Assume it's a valid By string like By.XPATH that wasn't caught
        return by  # It's already a By object

    def include_jquery(self, driver):
        jquery_path = os.path.join(self.includes_path, 'jquery.js')
        try:
            with open(jquery_path, 'r', errors='ignore') as f:
                driver.execute_script(f.read())
        except FileNotFoundError:
            self.log(f"jQuery file not found: {jquery_path}. Ensure it exists.", "error")
        except Exception as e:
            self.log(f"Error loading jQuery from {jquery_path}: {e}", "error")

    def get_account(self, site, number=None):
        return self.accounts[site][number] if number is not None else self.accounts[site]

    def get_sharing_account(self, username=None):
        expected_dev_path = os.path.join(os.path.expanduser("~"), 'Git', 'CreateThread', 'source')
        is_dev_env = (os.getenv('PC_USERNAME') in self.home and self.path == expected_dev_path)

        if username != USERNAME_3 and is_dev_env:
            self.log(f'Invalid username: {username} in {os.getenv("PC_USER").capitalize()} dev environment context')
            self.quit()

        if isinstance(username, int):
            return self.accounts[SITE_SHARING][username]
        if isinstance(username, str):
            if username == USERNAME_3:
                return self.accounts[SITE_SHARING][3]
            for acc_index, acc in enumerate(self.accounts[SITE_SHARING]):  # Iterate with index
                if acc.get('username') == username:
                    return self.accounts[SITE_SHARING][acc_index]  # Return the specific account
            self.log(f"Sharing account for username '{username}' not found, returning default.", "warning")
            return self.accounts[SITE_SHARING][0]
        return self.accounts[SITE_SHARING]

    def run_js(self, command, return_data=False):
        if return_data:
            command = f'return {command}'
        return self.driver.execute_script(command)

    def sleep(self, start, to=0):
        if to != 0:
            sleep_duration = uniform(start, to)
        else:
            sleep_duration = start

        if sleep_duration >= 300:
            self.log(f'Sleeping for {round(sleep_duration)} seconds')
            for remaining in range(round(sleep_duration), 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write("{:2d} seconds remaining".format(remaining))
                sys.stdout.flush()
                time.sleep(1)
                if remaining % 600 == 0:
                    self.log(f'Still sleeping for {round(remaining)} seconds')
            sys.stdout.write("\rDone sleeping.                                  \n")
            self.log('-----------------------------------------------')
        else:
            time.sleep(sleep_duration)

    def create_folder(self, path_to_create):
        if not os.path.isdir(path_to_create):
            try:
                os.makedirs(path_to_create, exist_ok=True)
            except OSError as e:
                self.log(f"Error creating folder {path_to_create}: {e}", "error")
        return path_to_create

    @staticmethod
    def get_folder_content(path_to_list):
        try:
            if os.path.isdir(path_to_list):
                return [f for f in os.listdir(path_to_list) if os.path.isfile(os.path.join(path_to_list, f))]
            else:
                print(f"Warning: Path is not a directory for get_folder_content: {path_to_list}")
                return []
        except FileNotFoundError:
            print(f"Warning: Folder not found for get_folder_content: {path_to_list}")
            return []
        except Exception as e:
            print(f"Error in get_folder_content for {path_to_list}: {e}")
            return []

    def set_log_callback(self, callback):
        self.log_callback = callback

    def log(self, message, log_type='info'):
        if self.log_callback:
            self.log_callback(message)

        if self.logger:  # Ensure logger is initialized
            if log_type == 'error':
                self.logger.error(message)
            elif log_type == 'warning':
                self.logger.warning(message)
            else:
                self.logger.info(message)
        else:  # Fallback if logger somehow isn't ready (should not happen)
            print(f"[{log_type.upper()}] {message}")

    def reset(self):
        self.downloads = {}
        self.log('Clear temporary folders')
        if self.downloadPath: self.clear_directory(self.downloadPath)
        if self.temp_images_path: self.clear_directory(self.temp_images_path)

    @staticmethod
    def clear_directory(directory_path):
        if not os.path.isdir(directory_path):
            return
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def setup_logger(self):
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_file_path = os.path.join(self.path, 'log.txt')

        logger_name = f"GlobalvarLogger_{self.selected_username if self.selected_username else 'default'}"
        logger = logging.getLogger(logger_name)

        logger.setLevel(logging.INFO)

        if not logger.handlers:
            try:
                handler = RotatingFileHandler(log_file_path, maxBytes=90000000, backupCount=5, encoding='utf-8')
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            except Exception as e:
                print(f"Error setting up file logger at {log_file_path}: {e}. Logging to console.")
                if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
                    console_handler = logging.StreamHandler(sys.stdout)
                    console_handler.setFormatter(formatter)
                    logger.addHandler(console_handler)
        return logger

    def quit(self, only_driver=False):
        self.log('Shutting down driver')
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.log(f"Error quitting driver: {e}", "error")
        if not only_driver:
            self.log('Shutting down application')
            sys.exit()

    def get_content_from_file(self, username, file_name):
        full_file_path = os.path.join(f'{self.threads_folder}_{username}', file_name)
        self.log(f'Reading file {full_file_path}')
        try:
            with open(full_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except FileNotFoundError:
            self.log(f"File not found: {full_file_path}", "error")
            return {
                'type': '', 'subject': '', 'body': '', 'tags': '', 'fileName': file_name, 'error': 'File not found'
            }
        except Exception as e:
            self.log(f"Error reading file {full_file_path}: {e}", "error")
            return {
                'type': '', 'subject': '', 'body': '', 'tags': '', 'fileName': file_name, 'error': str(e)
            }

        # Simplified parsing logic based on '|part|' delimiter
        parts = content.split('|part|')

        type_val, subject_val, body_val, tags_val = '', '', '', ''

        if len(parts) == 4:  # Expecting: type |part| subject |part| body |part| tags
            # The first part before any |part| is type
            # The part after the last |part| is tags
            # This assumes no |part| in the actual content of type, subject, body, tags.
            type_val = parts[0].strip().split('\n')[0]  # Get first line of first part as type
            subject_val = parts[1].strip()
            body_val = self.escape_chars(parts[2].replace('\n', '\\n').strip())  # escape_chars after potential newlines
            tags_val = parts[3].strip()
        elif len(parts) == 3:  # Expecting: subject |part| body |part| tags (type is hardcoded 'game')
            type_val = 'game'
            subject_val = parts[0].strip()
            body_val = self.escape_chars(parts[1].replace('\n', '\\n').strip())
            tags_val = parts[2].strip()
        else:
            self.log(
                f"Unexpected file format for {full_file_path}. Parts count: {len(parts)}. Content: '{content[:100]}...'",
                "warning")
            # Attempt to extract from lines if |part| split fails.
            lines = content.split('\n')
            if lines and lines[-1] == '': del lines[-1]
            if len(lines) >= 3:  # A very basic fallback
                type_val = lines[0]
                subject_val = lines[1]
                tags_val = lines[-1]
                body_val = self.escape_chars('\\n'.join(lines[2:-1]))

        return {
            'type': type_val,
            'subject': subject_val,
            'body': body_val,
            'tags': tags_val,
            'fileName': file_name
        }

    @staticmethod
    def escape_chars(text):
        text = text.replace(' ', ' ')
        text = text.replace("\\", "\\\\")
        text = text.replace('"', '\\"')
        return text

    def remove_file(self, file_name, username):
        base_folder = os.path.join(self.home, f'Threads_{username}')
        full_path = os.path.join(base_folder, file_name)

        self.log(f'Attempting to process file: {full_path}')

        if os.path.exists(full_path):
            if username == USERNAME_3:
                done_folder = os.path.join(base_folder, 'done')
                self.create_folder(done_folder)

                destination_path = ''
                try:
                    destination_path = os.path.join(done_folder, os.path.basename(file_name))
                    shutil.move(full_path, destination_path)
                    self.log(f'Moved file to: {destination_path}')
                except Exception as e:
                    self.log(f"Error moving file {full_path} to {destination_path}: {e}", "error")
            else:
                try:
                    os.remove(full_path)
                    self.log(f'Removed file: {full_path}')
                except OSError as e:
                    self.log(f"Error removing file {full_path}: {e}", "error")
        else:
            self.log(f"File not found for removal/move: {full_path}", "warning")

    @staticmethod
    def get_time():
        now = datetime.now()
        return now.strftime("%H:%M:%S")

    @staticmethod
    def regex_group(string, regex_pattern):
        matches = re.finditer(regex_pattern, string, re.MULTILINE | re.IGNORECASE)
        groups = []
        for match in matches:
            groups.append(match.group(0))
        return groups

    def get_source(self):
        return self.driver.page_source

    def fix_links(self, data):
        host_names = HOST_NAMES.copy()
        if self.update and not self.update_all:
            if HOST_NAME_DDOWNLOAD in HOST_NAMES:
                host_names.remove(HOST_NAME_DDOWNLOAD)

        for host in host_names:
            for comment in data['links'][host].keys():
                while True:
                    if len(data['links'][host][comment]) != len(data['links'][HOST_NAME_RAPIDGATOR][comment]):
                        self.log(f'Fix {host} links')
                        if comment not in self.downloads.keys():
                            link_group = 'Default Links' if comment == '#' else comment
                            self.log(f'Download: {link_group}')
                            self.rapidgator.download(data['links'][HOST_NAME_RAPIDGATOR], comment)

                        self.log(f'Upload files to {host}')
                        try:
                            data['links'][host][comment] = getattr(getattr(self, host), 'upload')(self.downloads[comment])
                            source_length = len(data['links'][HOST_NAME_RAPIDGATOR][comment])
                            host_length = len(data['links'][host][comment])
                            if source_length != host_length:
                                self.reset()
                                raise LinkCountMismatchException(source_length, host_length)
                            self.hcapital.edit_links(data['links'], False)
                            self.hcapital.edit_links(data['links'], True)
                        except LinkCountMismatchException as e:
                            self.reset()
                        except Exception as e:
                            data['links'][host][comment] = []
                            print(e)
                        except BaseException as e:
                            data['links'][host][comment] = []
                            print(e)
                    break

class LinkCountMismatchException(Exception):
    def __init__(self, len_a, len_b):
        super().__init__(f"Unequal number of links: list a has {len_a} links, list b has {len_b} links.")


glv = Globalvar()