import os
import json
import logging
import boto3
import psycopg2
import pandas as pd


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

file_handler = logging.FileHandler("RedShift_Library.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class RedShiftTool(object):
    """This class handle most of the interaction needed with RedShift,
    so the base code becomes more readable and straightforward."""
    
    def __init__(self, connect_file, connect_by_cluster=True, fail_silently=False):
        # Code structure based on StackOverFlow answer
        # https://stackoverflow.com/questions/44243169/connect-to-redshift-using-python-using-iam-role

        # Getting credential files path
        try:
            credentials_path = os.environ["CREDENTIALS_HOME"]
            logger.debug(f"Environment Variable found: {credentials_path}")
        except KeyError:
            credentials_path = ""
            logger.warning("Environment Not Variable found")
        finally:
            connect_file = os.path.join(credentials_path, connect_file)

        logger.debug(f"connect_by_cluster = {connect_by_cluster}")
        if connect_by_cluster:

            with open(connect_file) as cf:
                config = json.load(cf)
            logger.debug("Configuration file found and read!")

            client = boto3.client('redshift')
            logger.debug("Connected to RedShift by boto3")

            logger.debug("Getting cluster credentials...")
            cluster_creds = client.get_cluster_credentials(DbUser=config["user"],
                                                            DbName=config["dbname"],
                                                            ClusterIdentifier=config["cluster_id"],
                                                            AutoCreate=False)
            logger.debug("Cluster credentials responded.")

        else:
            with open(connect_file) as cf:
                config = json.load(cf)

        self.dbname = config["dbname"]
        self.user = config["user"]
        self.password = config.get("password")
        self.cluster_id = config.get("cluster_id")
        self.host = config["host"]
        self.port = config["port"]
        self.cluster_creds = cluster_creds
        self.connect_by_cluster = connect_by_cluster

        self.connection = self.connect(fail_silently)
        self.cursor = self.connection.cursor()

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
            return conn
        
        except psycopg2.Error as e:
            print('Failed to open database connection.')
            logger.exception('Failed to open database connection.')
            
            if not fail_silently:
                raise e
            else:
                logger.error("ATENTION: Failing Silently")

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

    # def unload_to_S3(self, redshift_query, s3_bucket_path, filename):
    #     unload_query = """
    #         UNLOAD ('{redshift_query}')
    #         TO 's3://{s3_bucket}/{s3_key}/{table}_'
    #         with credentials
    #         'aws_access_key_id={access_key};aws_secret_access_key={secret_key}'
    #         {unload_options};
    #         """.format(redshift_query=redshift_query,
    #                    table=self.table,
    #                    s3_bucket=self.s3_bucket,
    #                    s3_key=self.s3_key,
    #                    access_key=credentials.access_key,
    #                    secret_key=credentials.secret_key,
    #                    unload_options=unload_options)

    #     self.execute_sql(unload_query)

    def close_connection(self):
        """Closes Connection with RedShift database"""
        
        self.connection.close()
        logger.info("Connection closed.")


def test():
    snowplow_revelo = RedShiftTool(connect_file="redshift_IAM.json")
    
    sql_test_query = """SELECT * FROM atomic.Events LIMIT 10"""

    table = snowplow_revelo.query(sql_test_query, fetch_through_pandas=False)
    print("Query Result by fetchall command:")
    print(table)

    print("")

    print("Query Result by pandas:")
    df = snowplow_revelo.query(sql_test_query, fail_silently=False)
    print(df)

    snowplow_revelo.close_connection()


if __name__ == '__main__':
    test()
