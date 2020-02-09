import mysql.connector


class ConnectionError(Exception):
    """A custom 'empty' class that inherits from the Exception class
       to deal with Database connection issues"""
    pass


class CredentialsError(Exception):
    """A custom 'empty' class that inherits from the Exception class
       to deal with any login issues"""
    pass


class SQLError(Exception):
    """A custom 'empty' class that inherits from the Exception class"""
    pass


class UseDatabase:
    """UseDatabase - Database Context Manager Class"""

    def __init__(self, config: dict = dict()) -> None:
        """Initialize Database Characteristics"""

        self.configuration = config

    def __enter__(self) -> 'cursor':
        """Connect to the database and create a cursor"""

        # This function executes as the with statement starts.

        try:
            # open connection
            self.conn = mysql.connector.connect(**self.configuration)

            # create cursor handle
            self.cursor = self.conn.cursor()

            return self.cursor

        except mysql.connector.errors.InterfaceError as err:
            raise ConnectionError(err)
        except mysql.connector.errors.ProgrammingError as err:
            raise CredentialsError(err)

    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        """This function is guaranteed to execute whenever the with's suite terminates;
           Commits changes and close database connection"""

        self.conn.commit()
        self.cursor.close()
        self.conn.close()

        # Check for exceptions that occurred after executing commit and close methods.
        # Check if exc_type is a connector.errors.ProgrammingError
        if exc_type is mysql.connector.errors.ProgrammingError:
            raise SQLError(exc_value)
        # Or if any other excception occurred
        elif exc_type:
            raise exc_type(exc_value)
