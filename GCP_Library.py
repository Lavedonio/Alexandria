import os
import json
import logging
import pandas as pd
from google.cloud import bigquery


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

LOG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "GCP_Library.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class GCPTool(object):
    """This class handle most of the interaction needed with Google Cloud Platform,
    so the base code becomes more readable and straightforward."""
    
    def __init__(self, connect_file, init_list=[]):
        # Code created following Google official API documentation:
        # https://cloud.google.com/bigquery/docs/reference/libraries
        # https://cloud.google.com/bigquery/docs/quickstarts/quickstart-client-libraries?hl=pt-br#bigquery_simple_app_query-python

        # Checking if no client is instantiated
        if len(init_list) == 0:
            logger.error("ERROR: No client instantiated on 'init_list' class initialization parameter")
            raise ValueError("No client instantiated on 'init_list' class initialization parameter")

        # Getting credential files path
        try:
            credentials_path = os.environ["CREDENTIALS_HOME"]
            logger.debug(f"Environment Variable found: {credentials_path}")
        except KeyError:
            credentials_path = ""
            logger.warning("Environment Not Variable found")
        finally:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(credentials_path, connect_file)

        # Default values
        bq_client = None

        if "bigquery" in init_list:
            logger.debug("Initiating BigQuery Client")
            
            try:
                bq_client = bigquery.Client()
                logger.debug("Connected.")
            
            except Exception as e:
                logger.exception("Error connecting with BigQuery!")
                raise e

        self.bq_client = bq_client

    def query(self, sql_query):
        """Run a query and return the results as a Pandas Dataframe"""

        logger.debug(f"Initiating query: {sql_query}")
        try:
            result = self.bq_client.query(sql_query).to_dataframe()
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


def test():
    bq = GCPTool(connect_file="revelo-hebe-29868b4d02e4.json", init_list=["bigquery"])

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


if __name__ == '__main__':
    test()
