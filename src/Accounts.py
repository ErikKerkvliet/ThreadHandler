import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Assume these are imported from your existing hosts.Host module
# If they are in the same file, you can define them here directly.
# For this example, I'll define them for completeness.
HOST_NAME_RAPIDGATOR = 'rapidgator'
HOST_NAME_FICHIER = '1fichier'  # Original used 'FICHIER', mapping to 'FICHIER' in .env
HOST_NAME_MEXASHARE = 'mexashare'
HOST_NAME_KATFILE = 'katfile'
HOST_NAME_DDOWNLOAD = 'ddownload'
HOST_NAME_ROSEFILE = 'rosefile'
HOST_NAME_FIKPER = 'fikper'
HOST_NAME_LOCALHOST = 'localhost'
HOST_NAME_FILE = 'file.al'  # Original used 'FILE', mapping to 'FILE' in .env
HOST_NAME_SABERCAT = 'sabercat'

# Account type constants
ANIME_SHARING = 'sharing'  # maps to ANIME_SHARING in .env
IWTF = 'iwanttf'  # maps to IWTF in .env
TURBO_IMAGE = 'turbo_image'  # maps to TURBO_IMAGE in .env


def _get_env_accounts(service_prefix: str, fields: list[str]) -> list[dict]:
    """
    Helper function to load a list of accounts for a service from environment variables.
    Example fields: ['username', 'password'] or ['email', 'password', 'api']
    """
    accounts = []
    index = 0
    while True:
        account_data = {}
        # Try to fetch the first field for the current index to see if the account exists
        first_field_env_var = f"{service_prefix.upper()}_{index}_{fields[0].upper()}"
        if os.getenv(
                first_field_env_var) is None and index > 0 and not accounts:  # check if even first account (index 0) for first field is missing
            break  # No more accounts for this service
        if os.getenv(
                first_field_env_var) is None and index > 0:  # if after first account, the next indexed account is missing its first field, stop
            break
        if os.getenv(
                first_field_env_var) is None and index == 0:  # If very first entry is missing, might be an error or no accounts
            has_any_field_for_index_0 = any(
                os.getenv(f"{service_prefix.upper()}_0_{field.upper()}") for field in fields)
            if not has_any_field_for_index_0:
                break  # No accounts defined for this service at all

        all_fields_present_for_current_account = True
        field = None
        for field in fields:
            env_var_name = f"{service_prefix.upper()}_{index}_{field.upper()}"
            value = os.getenv(env_var_name)
            if value is not None:
                account_data[field] = value
            elif field == fields[0]:  # If the primary field is missing, assume the account doesn't exist
                all_fields_present_for_current_account = False
                break
            # For other fields, if they are missing, they might be optional,
            # or it's an incomplete configuration.
            # For simplicity here, we assume if the first field is present, others are expected.
            # A more robust solution might mark certain fields as optional.
            # However, based on your original structure, all listed fields per account type are mandatory.

        if all_fields_present_for_current_account and account_data:
            accounts.append(account_data)
        elif not all_fields_present_for_current_account and field == fields[
            0] and index > 0:  # stop if first field of next account is missing
            break
        elif not account_data and index == 0:  # No data for the first account
            break

        index += 1
        # Safety break if we somehow get into an infinite loop (e.g., >100 accounts)
        if index > 100:
            print(f"Warning: Exceeded 100 account iterations for {service_prefix}. Breaking.")
            break

    return accounts


class Accounts:
    accounts = {
        ANIME_SHARING: _get_env_accounts(
            ANIME_SHARING,  # Uses 'ANIME_SHARING' as prefix in .env
            ['username', 'password']
        ),
        HOST_NAME_RAPIDGATOR: _get_env_accounts(
            HOST_NAME_RAPIDGATOR.upper(),  # .env prefix is RAPIDGATOR
            ['username', 'password']
        ),
        HOST_NAME_FICHIER: _get_env_accounts(
            'FICHIER',  # .env prefix is FICHIER (mapping from HOST_NAME_FICHIER)
            ['username', 'password']
        ),
        HOST_NAME_MEXASHARE: _get_env_accounts(
            HOST_NAME_MEXASHARE.upper(),  # .env prefix is MEXASHARE
            ['username', 'password']
        ),
        IWTF: _get_env_accounts(
            IWTF.upper(),  # .env prefix is IWTF
            ['username', 'password']
        ),
        HOST_NAME_LOCALHOST: _get_env_accounts(
            HOST_NAME_LOCALHOST.upper(),  # .env prefix is LOCALHOST
            ['host', 'username', 'password', 'database']
        ),
        HOST_NAME_KATFILE: _get_env_accounts(
            HOST_NAME_KATFILE.upper(),  # .env prefix is KATFILE
            ['username', 'password', 'api']
        ),
        HOST_NAME_ROSEFILE: _get_env_accounts(
            HOST_NAME_ROSEFILE.upper(),  # .env prefix is ROSEFILE
            ['username', 'email', 'password']
        ),
        HOST_NAME_DDOWNLOAD: _get_env_accounts(
            HOST_NAME_DDOWNLOAD.upper(),  # .env prefix is DDOWNLOAD
            ['username', 'password']
        ),
        HOST_NAME_FIKPER: _get_env_accounts(
            HOST_NAME_FIKPER.upper(),  # .env prefix is FIKPER
            ['email', 'password']
        ),
        HOST_NAME_FILE: _get_env_accounts(
            'FILE',  # .env prefix is FILE (mapping from HOST_NAME_FILE)
            ['email', 'password']
        ),
        HOST_NAME_SABERCAT: _get_env_accounts(
            HOST_NAME_SABERCAT.upper(),  # .env prefix is SABERCAT
            ['username', 'email', 'password']
        ),
        TURBO_IMAGE: _get_env_accounts(
            TURBO_IMAGE.upper(),  # .env prefix is TURBO_IMAGE
            ['username', 'email', 'password']
        ),
    }

    @staticmethod
    def get_accounts() -> dict:
        """
        Return a dictionary containing all account information categorized by service.
        """
        return Accounts.accounts