import pymysql
from sys import exit

# Constants for SQL query types
SELECT_QUERY = 'SELECT'
INSERT_QUERY = 'INSERT'
UPDATE_QUERY = 'UPDATE'
DELETE_QUERY = 'DELETE'

# Constants for account keys
ACCOUNT_HOST = 'host'
ACCOUNT_USERNAME = 'username'
ACCOUNT_PASSWORD = 'password'
ACCOUNT_DATABASE = 'database'


class DB:
    """Class to handle database operations"""

    def __init__(self, glv):
        """
        Initialize with a global object that will provide logging and account retrieval

        :param glv: Global object providing methods for logging and fetching account details
        """
        self.glv = glv
        self.connection = None

    def connect(self):
        """Establishes a connection to the database if not already connected"""
        if self.connection is None:
            self.glv.log('Making connection with the DB')
            account = self.glv.get_account('localhost', 0)
            self.connection = pymysql.Connection(
                host=account[ACCOUNT_HOST],
                user=account[ACCOUNT_USERNAME],
                password=account[ACCOUNT_PASSWORD],
                database=account[ACCOUNT_DATABASE]
            )
            if self.connection is not None:
                self.glv.log('Connection established')

    def get_entry_by_id(self, entry_id):
        """
        Retrieves a database entry by its ID

        :param entry_id: ID of the entry to retrieve
        :return: Result of the query
        """
        self.connect()
        query = f'SELECT * FROM entries WHERE id = {entry_id} and vndb_id != 0;'
        return self.run_query(query, error=False, output=False)

    def get_entries_by_romanji(self, romanji):
        """
        Retrieves database entries by romanji

        :param romanji: Romanji name of the entries to retrieve
        :return: Result of the query
        """
        self.connect()
        query = f'SELECT * FROM entries WHERE romanji = "{romanji}" and type="ova";'
        return self.run_query(query, error=False, output=False, full_result=True)

    def insert_row(self, table, data):
        """
        Inserts a new row into the specified table

        :param table: Name of the table to insert into
        :param data: Dictionary of column-value pairs to insert
        """
        self.connect()
        columns = ', '.join(data.keys())
        values = ', '.join(f"'{v}'" for v in data.values())
        query = f'INSERT INTO {table} ({columns}) VALUES ({values});'
        self.run_query(query)

    def edit_row(self, table, data, where):
        """
        Edits an existing row in the specified table

        :param table: Name of the table to update
        :param data: Dictionary of column-value pairs to update
        :param where: Condition for selecting the row to update
        """
        self.connect()
        values = ', '.join(f"`{k}` = '{v}'" for k, v in data.items())
        query = f'UPDATE {table} SET {values} WHERE {where};'
        self.run_query(query)

    def get_sharing_urls(self, entry, author=''):
        if self.connection is None:
            self.connect()

        if author != '':
            author = f' AND author = "{author}"'

        query = f'SELECT * FROM threads WHERE entry_id = {entry}{author}'
        result = self.run_query(query, False, False, True)

        result_dict = {}
        for row in result:
            dict_id = row[0]
            result_dict[dict_id] = {
                'id': row[0],
                'entry_id': row[1],
                'author': row[2],
                'number': row[3],
                'url': row[4],
            }

        return result_dict

    def check_for_thread(self, author):
        """
        Checks if a thread exists with the current global ID

        :return: Result of the query
        """
        self.connect()
        query = f'SELECT * FROM threads WHERE entry_id = {self.glv.id} AND author = "{author}"'
        result = self.run_query(query, error=True, output=False)
        return result

    def run_query(self, query, error=False, output=False, full_result=False):
        """
        Runs a SQL query

        :param query: SQL query to run
        :param error: Flag to indicate if errors should be returned
        :param output: Flag to indicate if query should be logged
        :param full_result: Flag to indicate if all results should be returned for SELECT queries
        :return: Result of the query or None
        """
        if output:
            self.glv.log(f'{query}')

        query_type = query[:6]

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)

                if query_type == INSERT_QUERY:
                    self.connection.commit()
                    table = query.split(' ')[2]
                    id_query = f'SELECT id FROM {table} ORDER BY id DESC LIMIT 1'
                    result = self.run_query(id_query)
                    return result

                elif query_type == SELECT_QUERY:
                    if full_result:
                        return cursor.fetchall()
                    else:
                        result = cursor.fetchone()
                        if isinstance(result, tuple):
                            return result[0]
                        return None

                elif query_type == UPDATE_QUERY or query_type == DELETE_QUERY:
                    self.connection.commit()

        except Exception as e:
            self.glv.log(e)
            if error:
                return e
            if SELECT_QUERY in query:
                return 0
            exit()
