import os

from dotenv import load_dotenv

load_dotenv()

SITE_SHARING = 'sharing'

USERNAME_1 = os.getenv('USER_KEY_1')
USERNAME_2 = os.getenv('USER_KEY_2')
USERNAME_3 = os.getenv('USER_KEY_3')
USERNAME_BOTH = 'Both'

USERNAMES = [
    USERNAME_1,
    USERNAME_2,
]
