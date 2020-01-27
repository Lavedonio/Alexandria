import os
import logging
import boto3
import psycopg2
import pandas as pd
from .General_Tools import fetch_credentials


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "RedShift_Library.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class RedShiftTool(object):
    """This class handle most of the interaction needed with RedShift,
    so the base code becomes more readable and straightforward."""

    def __init__(self, connect_by_cluster=True):
        # Code structure based on StackOverFlow answer
        # https://stackoverflow.com/questions/44243169/connect-to-redshift-using-python-using-iam-role

        # Getting credentials
        connection_type = "cluster_credentials" if connect_by_cluster else "master_password"
        logger.debug(f"connection_type = {connection_type}")

        redshift_creds = fetch_credentials(service_name="RedShift", connection_type=connection_type)
        aws_creds = fetch_credentials("AWS")

        # Getting cluster credentials
        if connect_by_cluster:
            client = boto3.client('redshift')
            logger.debug("Connected to RedShift by boto3")

            logger.debug("Getting cluster credentials...")
            cluster_creds = client.get_cluster_credentials(DbUser=redshift_creds["user"],
                                                           DbName=redshift_creds["dbname"],
                                                           ClusterIdentifier=redshift_creds["cluster_id"],
                                                           AutoCreate=False)
            logger.debug("Cluster credentials responded.")

        self.dbname = redshift_creds["dbname"]
        self.user = redshift_creds["user"]
        self.password = redshift_creds.get("password")
        self.cluster_id = redshift_creds.get("cluster_id")
        self.host = redshift_creds["host"]
        self.port = redshift_creds["port"]
        self.cluster_creds = cluster_creds
        self.connect_by_cluster = connect_by_cluster
        self.access_key = aws_creds["access_key"]
        self.secret_key = aws_creds["secret_key"]

        # Attibutes ready to be set in connection
        self.connection = None
        self.cursor = None

    def connect(self, fail_silently=False):
        """Create the connection using the __init__ attributes.
        If fail_silently parameter is set to True, any errors will be surpressed and not stop the code execution."""

        if self.connect_by_cluster:
            logger.debug("Connecting by cluster...")
            user = self.cluster_creds['DbUser']
            password = self.cluster_creds['DbPassword']
        else:
            logger.debug("Connecting by MasterUser and password...")
            user = self.user
            password = self.password

        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=user,
                password=password,
                database=self.dbname
            )
            logger.info("Connected!")

            self.connection = conn
            self.cursor = self.connection.cursor()
            return self

        except psycopg2.Error as e:
            print('Failed to open database connection.')
            logger.exception('Failed to open database connection.')

            if not fail_silently:
                raise e
            else:
                logger.error("ATENTION: Failing Silently")

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

    def unload_to_S3(self, redshift_query, s3_path, filename, unload_options="MANIFEST GZIP ALLOWOVERWRITE REGION 'us-east-2'"):

        if s3_path.endswith("/"):
            s3_path = s3_path[:-1]

        unload_query = f"""
            UNLOAD ($$ {redshift_query} $$)
            TO '{s3_path}/{filename}_'
            WITH CREDENTIALS
            'aws_access_key_id={self.access_key};aws_secret_access_key={self.secret_key}'
            {unload_options};
        """

        logger.debug("Unloading Query...")
        self.execute_sql(unload_query)

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


def test(using_with_statement=True):

    sql_test_query = """SELECT * FROM atomic.Events LIMIT 10"""

    timestamp = '2019-11-29 19:31:42.766000+00:00'
    extraction_query = """SELECT * FROM atomic.Events WHERE etl_tstamp = '{timestamp}'""".format(timestamp=timestamp)

    s3_path = "s3://revelo-redshift-data/new/"
    filename = "fausto"

    if using_with_statement:
        with RedShiftTool() as snowplow_revelo:
            table = snowplow_revelo.query(sql_test_query, fetch_through_pandas=False)
            print("Query Result by fetchall command:")
            print(table)

            print("")

            df = snowplow_revelo.query(sql_test_query, fail_silently=False)
            print("Query Result by pandas:")
            print(df)

            snowplow_revelo.unload_to_S3(extraction_query, s3_path, filename)

    else:
        snowplow_revelo = RedShiftTool()
        snowplow_revelo.connect()

        table = snowplow_revelo.query(sql_test_query, fetch_through_pandas=False)
        print("Query Result by fetchall command:")
        print(table)

        print("")

        df = snowplow_revelo.query(sql_test_query, fail_silently=False)
        print("Query Result by pandas:")
        print(df)

        snowplow_revelo.unload_to_S3(extraction_query, s3_path, filename)

        snowplow_revelo.close_connection()


if __name__ == '__main__':
    test()
