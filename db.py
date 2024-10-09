import sqlite3
class DB:
    def __init__(self, fileName):
        self.__fileName = fileName

    def _connectDB(self):
        return sqlite3.connect(self.__fileName)
    
    def select(self, query, args=None):
        try:
            with self._connectDB() as connection:
                cursor = connection.cursor()
                if args:
                    cursor.execute(query,args)
                else:
                    cursor.execute(query)
                records = cursor.fetchall()
                return records
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def insert(self, query, args):
        if args is None:
            print("Args can not be type None")
            return
        try:
            with self._connectDB() as connection:
                cursor = connection.cursor()
                cursor.execute(query, args)
                connection.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def delete(self, query, args):
        try:
            with self._connectDB() as connection:
                cursor = connection.cursor()
                cursor.execute(query, args)
                connection.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def update(self, query, args=None):
        try:
            with self._connectDB() as connection:
                cursor = connection.cursor()
                if args:
                    cursor.execute(query,args)
                else:
                    cursor.execute(query)
                connection.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None