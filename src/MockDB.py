import requests
import os

class MockDB:
    """Class to handle database operations"""

    def __init__(self, glv):
        self.glv = glv

    @staticmethod
    def get_entry_by_id(entry_id):
        return 0

    def insert_row(self, table, thread_data):
        data = {
            'v': 2,
            'EntryAction': 'updateSharingUrl',
            'entry': thread_data['entry_id'],
            'author': thread_data['author'],
            'url': thread_data['url'],
        }
        requests.post('http://hcapital.tk/index.php', data=data)

        self.add_to_thread_insert_file(data)

    @staticmethod
    def get_sharing_urls(entry, author=''):
        return []

    @staticmethod
    def check_for_thread(author):
        return None

    def add_to_thread_insert_file(self, data):
        columns = ', '.join(data.keys())
        values = ', '.join(f"'{v}'" for v in data.values())
        query = f'INSERT INTO threads ({columns}) VALUES ({values});'

        query_file = f'{self.glv.home}/thread_inserts.sql'
        if os.path.exists(query_file):
            with open(query_file, 'a') as file:
                file.write(query + '\n')
        else:
            with open(query_file, 'w') as file:
                file.write(query + '\n')
