import os
import logging
import boto3
import psycopg2
from .general_tools import fetch_credentials
from .sql_tools import PostgreSQLTool


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "redshift_tools.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class RedShiftTool(PostgreSQLTool):
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

        # Not used, but making it compatible with inherited class
        self.filename = None

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

    def unload_to_S3(self, redshift_query, s3_path, filename, unload_options="MANIFEST GZIP ALLOWOVERWRITE REGION 'us-east-2'"):
        """Executes an unload command in RedShift database to copy data to S3.
        Takes the parameters redshift_query to grab the data, s3_path to set the location of copied data,
        filename as the custom prefix of the file and unload options.

        Unload options can be better understood in this link:
        https://docs.aws.amazon.com/redshift/latest/dg/r_UNLOAD.html
        """

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
