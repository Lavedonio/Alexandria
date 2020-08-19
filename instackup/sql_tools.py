import os
import logging
import sqlite3
import psycopg2
import pandas as pd
from .general_tools import fetch_credentials


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "sql_tools.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class SQLTool(object):
    """Base class for the different types of SQL databases."""

    def __init__(self, sql_type, filename=None, connection='default'):
        if sql_type == "SQLite":
            sql_creds = {}
            if filename is None:
                filename = ':memory:'
        else:
            # Getting credentials
            sql_creds = fetch_credentials(service_name=sql_type, connection=connection)

        self.sql_type = sql_type

        # SQLite
        self.filename = filename

        # PostgreSQL and others
        self.dbname = sql_creds.get("dbname")
        self.user = sql_creds.get("user")
        self.password = sql_creds.get("password")
        self.host = sql_creds.get("host")
        self.port = sql_creds.get("port")

        # Attibutes ready to be set in connection
        self.connection = None
        self.cursor = None

    def connect(self, fail_silently=False):
        """Create the connection using the __init__ attributes.

        If fail_silently parameter is set to True, any errors will be surpressed
        and not stop the code execution.
        """

        try:
            if self.sql_type == "SQLite":
                conn = sqlite3.connect(self.filename)
            else:
                conn = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.dbname
                )
            logger.info("Connected!")
        except (sqlite3.Error, psycopg2.Error) as e:
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

        If fail_silently parameter is set to True, any errors will be surpressed
        and not stop the code execution.
        """

        try:
            self.cursor.execute(command)
            logger.debug(f"Command Executed: {command}")

        except (sqlite3.Error, psycopg2.Error) as e:
            logger.exception("Error running command!")

            if not fail_silently:
                raise e
            else:
                logger.error("ATENTION: Failing Silently")

    def query(self, sql_query, fetch_through_pandas=True, fail_silently=False):
        """Run a query and return the results.

        fetch_through_pandas parameter tells if the query should be parsed by the cursor or pandas.
        If fail_silently parameter is set to True, any errors will be surpressed
        and not stop the code execution.

        Returns either a DataFrame (if fetch_through_pandas parameter is set to True)
        or a list of tuples, each representing a row, with their position in the same order
        as in the columns of the SELECT statement in the sql_query parameter.
        """

        # Eliminating SQL table quotes that can't be handled by PostgreSQL
        sql_query = sql_query.replace("`", "")

        if fetch_through_pandas:
            try:
                result = pd.read_sql_query(sql_query, self.connection)

            except (sqlite3.Error, psycopg2.Error, pd.io.sql.DatabaseError) as e:
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

            except (sqlite3.Error, psycopg2.Error) as e:
                logger.exception("Error running query!")
                result = None

                if not fail_silently:
                    raise e
                else:
                    logger.error("ATENTION: Failing Silently")

        return result

    def close_connection(self):
        """Closes Connection with the database"""
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


class SQLiteTool(SQLTool):
    """This class handle most of the interaction needed with SQLite3 databases,
    so the base code becomes more readable and straightforward."""

    def __init__(self, filename=None):
        super().__init__("SQLite", filename=filename)

    def describe_table(self, table, fetch_through_pandas=True, fail_silently=False):
        """Special query that returns all metadata from a specific table"""

        sql_query = f"""SELECT name FROM sqlite_master WHERE type='{table}';"""
        return self.query(sql_query, fetch_through_pandas=fetch_through_pandas, fail_silently=fail_silently)


class PostgreSQLTool(SQLTool):
    """This class handle most of the interaction needed with PostgreSQL databases,
    so the base code becomes more readable and straightforward."""

    def __init__(self, connection='default'):
        super().__init__("PostgreSQL", connection=connection)

    def describe_table(self, table, schema="public", fetch_through_pandas=True, fail_silently=False):
        """Special query that returns all metadata from a specific table"""

        sql_query = f"""SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE table_schema='{schema}' AND table_name='{table}'"""
        return self.query(sql_query, fetch_through_pandas=fetch_through_pandas, fail_silently=fail_silently)

    def get_all_db_info(self, get_json_info=True, fetch_through_pandas=True, fail_silently=False):
        """Gets all Database info, using a INFORMATION_SCHEMA query.
        Ignore table pg_stat_statements and tables inside schemas pg_catalog and information_schema.

        If get_json_info parameter is True, it adds 2 columns with the data types from each key
        inside json and jsonb columns.

        fetch_through_pandas and fail_silently parameters are passed directly to the query method if
        get_json_info parameter is set to False; if it's not, these 2 parameters are passed as their default values.

        Returns a DataFrame if either get_json_info or fetch_through_pandas parameters are set to True;
        otherwise returns a list of tuples, each representing a row, with their position in the same order
        as in the columns of the INFORMATION_SCHEMA.COLUMNS table.
        """

        sql_query = """SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name != 'pg_stat_statements' AND table_schema NOT IN ('pg_catalog', 'information_schema')"""

        if not get_json_info:
            return self.query(sql_query, fetch_through_pandas=fetch_through_pandas, fail_silently=fail_silently)
        else:
            df = self.query(sql_query, fetch_through_pandas=True, fail_silently=False)

            # Adding 2 new empty columns for the JSON data
            num_rows, _ = df.shape
            col_add_position = df.columns.get_loc("data_type")
            df.insert(col_add_position + 1, 'json_key', pd.Series(["" for i in range(num_rows)], index=df.index))
            df.insert(col_add_position + 2, 'json_value_type', pd.Series(["" for i in range(num_rows)], index=df.index))

            # Filtering only json and jsonb types for further info lookup
            df_json = df[df['data_type'].isin(['jsonb', 'json'])]

            # Creating a empty dictionary list that will be later converted to a DataFrame and
            # joined with the base information_schema query. It's done that way to improve efficiency
            json_types_dict = {}
            for index in df_json.columns.values.tolist():
                json_types_dict[index] = []

            # Base query for JSON keys and value data type lookup
            json_query = """
                SELECT
                    json_data.key,
                    {json}_typeof(json_data.value) AS json_value_data_type,
                    COUNT(*)
                FROM {schema}.{table}, {json}_each({table}.{column}) AS json_data
                GROUP BY 1, 2
                ORDER BY 1, 2;
            """

            # Run the base query for each column with json or jsonb data types
            # and add the results to the json_types_dict.
            for index, row in df_json.iterrows():
                df_query_results = self.query(json_query.format(
                    schema=row['table_schema'],
                    table=row['table_name'],
                    column=row['column_name'],
                    json=row['data_type'],
                ), fetch_through_pandas=True, fail_silently=False)

                for _, query_row in df_query_results.iterrows():
                    for col in json_types_dict.keys():
                        if col not in ['json_key', 'json_value_type']:
                            json_types_dict[col].append(row[col])
                    json_types_dict['json_key'].append(query_row['key'])
                    json_types_dict['json_value_type'].append(query_row['json_value_data_type'])

            # Converting the results to DataFrame, joining and sorting them before returning the result
            new_df = pd.concat([df, pd.DataFrame(json_types_dict)], ignore_index=True)
            return new_df.sort_values(by=['table_catalog', 'table_schema', 'table_name', 'column_name', 'data_type', 'json_key', 'json_value_type'], ignore_index=True)
