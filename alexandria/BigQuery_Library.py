import os
import logging
from google.cloud import bigquery
from google.cloud import bigquery_datatransfer_v1
from google.protobuf.timestamp_pb2 import Timestamp
from .General_Tools import fetch_credentials


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "BigQuery_Library.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class BigQueryTool(object):
    """This class handle most of the interaction needed with BigQuery,
    so the base code becomes more readable and straightforward."""

    def __init__(self):
        # Code created following Google official API documentation:
        # https://cloud.google.com/bigquery/docs/reference/libraries
        # https://cloud.google.com/bigquery/docs/quickstarts/quickstart-client-libraries?hl=pt-br#bigquery_simple_app_query-python

        # Getting credentials
        google_creds = fetch_credentials("Google")
        connect_file = google_creds["secret_filename"]
        credentials_path = fetch_credentials("credentials_path")

        # Sets environment if not yet set
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") is None:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(credentials_path, connect_file)

        # Initiating client
        logger.debug("Initiating BigQuery Client")
        try:
            bq_client = bigquery.Client()
            logger.debug("Connected.")
        except Exception as e:
            logger.exception("Error connecting with BigQuery!")
            raise e

        self.client = bq_client
        self.transfer_client = None

    def query(self, sql_query):
        """Run a query and return the results as a Pandas Dataframe"""

        logger.debug(f"Initiating query: {sql_query}")
        try:
            result = self.client.query(sql_query).to_dataframe()
            logger.debug("Query returned successfully.")

        except AttributeError as ae:
            logger.exception("BigQuery client not initialized")
            print("\n------\nERROR: BigQuery client not initialized\n------\n")
            raise ae

        except Exception as e:
            logger.exception("Query failed")
            raise e

        return result

    def upload(self, dataframe, dataset, table, if_exists='fail'):
        """Executes an insert SQL command into BigQuery

        if_exists can take 3 different arguments:
            'fail': If table exists, raises error.
            'replace': If table exists, drop it, recreate it, and insert data.
            'append': If table exists, insert data. Create if does not exist.

        Full documentation for Pandas export to BigQUery can be found here:
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_gbq.html
        """

        destination = dataset + "." + table
        dataframe.to_gbq(destination, chunksize=None, if_exists=if_exists)

    def start_transfer(self, project_path):
        """Trigger a transfer to start executing in BigQuery Transfer."""

        # Initiating client
        self.transfer_client = bigquery_datatransfer_v1.DataTransferServiceClient()

        # Getting current timestamp so it starts now.
        # Google documentation: https://developers.google.com/protocol-buffers/docs/reference/csharp/class/google/protobuf/well-known-types/timestamp
        # StackOverflow answer: https://stackoverflow.com/questions/49161633/how-do-i-create-a-protobuf3-timestamp-in-python
        timestamp = Timestamp()
        timestamp.GetCurrentTime()

        # Triggering transfer
        response = self.transfer_client.start_manual_transfer_runs(parent=project_path, requested_run_time=timestamp)

        # Parse response to get state parameter
        state_location = str(response).find("state: ")
        state_param = str(response)[state_location:].split("\n", 1)[0]
        state = state_param.replace("state: ", "")

        return state


def test():
    bq = BigQueryTool()

    sql_test_query = """SELECT MAX(etl_tstamp) FROM `revelo-hebe.source_fausto.atomic_events`"""

    sql_query = """
    SELECT
      users.id,
      users.email,
      users.company_id,
      ga_signup.datehour,
      -- ga_signup.dimension4,
      ga_signup.source,
      ga_signup.medium,
      ga_signup.campaign,
      ga_signup.keyword,
      ga_signup.adcontent,
      ga_signup.goal9completions
    FROM
      `revelo-hebe.source_revelo_internal.users` users
      RIGHT JOIN `revelo-hebe.source_ga_signup_company_id.report` ga_signup ON CAST(users.id AS STRING) = ga_signup.dimension4
    WHERE
      users.employer = true"""

    df = bq.query(sql_query)
    print(df)

    dataset = "company"
    table = "signup"

    bq.upload(df, dataset, table)

    transfer_config = "projects/118480078918/transferConfigs/5e35261a-0000-2d5a-bd96-24058872d28c"
    print("Starting transfer...")
    state_response = bq.start_transfer(project_path=transfer_config)
    print(f"Transfer status: {state_response}")


if __name__ == '__main__':
    test()
