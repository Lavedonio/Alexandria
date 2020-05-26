import os
import logging
import psycopg2
import pandas as pd
from .general_tools import fetch_credentials


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "postgresql_tools.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class PostgreSQLTool(object):
    """This class handle most of the interaction needed with PostgreSQL databases,
    so the base code becomes more readable and straightforward."""

    def __init__(self, connection='default'):
        # Getting credentials
        postgresql_creds = fetch_credentials(service_name="RedShift", connection=connection)

        self.dbname = postgresql_creds["dbname"]
        self.user = postgresql_creds["user"]
        self.password = postgresql_creds["password"]
        self.host = postgresql_creds["host"]
        self.port = postgresql_creds["port"]

        # Attibutes ready to be set in connection
        self.connection = None
        self.cursor = None

    def connect(self, fail_silently=False):
        """Create the connection using the __init__ attributes.
        If fail_silently parameter is set to True, any errors will be surpressed and not stop the code execution."""

        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.dbname
            )
            logger.info("Connected!")
        except psycopg2.Error as e:
            print('Failed to open database connection.')
            logger.exception('Failed to open database connection.')

            if not fail_silently:
                raise e
            else:
                logger.error("ATENTION: Failing Silently")
        else:
            self.connection = conn
            self.cursor = self.connection.cursor()
            return self

    def commit(self):
        """Commit any pending transaction to the database."""
        self.connection.commit()
        logger.info("Transaction commited.")

    def rollback(self):
        """Roll back to the start of any pending transaction."""
        self.connection.rollback()
        logger.info("Roll back current transaction.")

    def execute_sql(self, command, fail_silently=False):
        """Execute a SQL command (CREATE, UPDATE and DROP).
        If fail_silently parameter is set to True, any errors will be surpressed and not stop the code execution."""

        try:
            self.cursor.execute(command)
            logger.debug(f"Command Executed: {command}")

        except psycopg2.Error as e:
            logger.exception("Error running command!")

            if not fail_silently:
                raise e
            else:
                logger.error("ATENTION: Failing Silently")

    def query(self, sql_query, fetch_through_pandas=True, fail_silently=False):
        """Run a query and return the results.
        fetch_through_pandas parameter tells if the query should be parsed by psycopg2 cursor or pandas.
        If fail_silently parameter is set to True, any errors will be surpressed and not stop the code execution."""

        # Eliminating SQL table quotes that can't be handled by RedShift
        sql_query = sql_query.replace("`", "")

        if fetch_through_pandas:
            try:
                result = pd.read_sql_query(sql_query, self.connection)

            except (psycopg2.Error, pd.io.sql.DatabaseError) as e:
                logger.exception("Error running query!")
                result = None

                if not fail_silently:
                    raise e
                else:
                    logger.error("ATENTION: Failing Silently")

        else:
            try:
                self.cursor.execute(sql_query)
                logger.debug(f"Query Executed: {sql_query}")

                result = self.cursor.fetchall()

            except psycopg2.Error as e:
                logger.exception("Error running query!")
                result = None

                if not fail_silently:
                    raise e
                else:
                    logger.error("ATENTION: Failing Silently")

        return result

    def decribe_table(self, table, schema="public", fetch_through_pandas=True, fail_silently=False):
        """Special query that returns all metadata from a specific table"""

        sql_query = f"""SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE table_schema='{schema}' AND table_name='{table}'"""
        return self.query(sql_query, fetch_through_pandas=fetch_through_pandas, fail_silently=fail_silently)

    def close_connection(self):
        """Closes Connection with RedShift database"""
        self.connection.close()
        logger.info("Connection closed.")

    # __enter__ and __exit__ functions for with statement.
    # With statement docs: https://docs.python.org/2.5/whatsnew/pep-343.html
    def __enter__(self):
        return self.connect()

    def __exit__(self, type, value, traceback):
        if traceback is None:
            # No exception, so commit
            self.commit()
        else:
            # Exception occurred, so rollback.
            self.rollback()
            # return False

        self.close_connection()
