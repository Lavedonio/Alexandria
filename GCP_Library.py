import os
import json
import logging
import pandas as pd
from google.cloud import bigquery


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

file_handler = logging.FileHandler("GCP_Library.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class GCPTool(object):
    """This class handle most of the interaction needed with Google Cloud Platform,
    so the base code becomes more readable and straightforward."""
    
    def __init__(self, connect_file, init_list=[]):
        # Code created following Google official API documentation:
        # https://cloud.google.com/bigquery/docs/reference/libraries

        # Getting credential files path
        try:
            credentials_path = os.environ["CREDENTIALS_HOME"]
            logger.debug(f"Environment Variable found: {credentials_path}")
        except KeyError:
            credentials_path = ""
            logger.warning("Environment Not Variable found")
        finally:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(credentials_path, connect_file)

        bq_client = None

        if "bigquery" in init_list:
            bq_client = bigquery.Client()

        self.bq_client = bq_client

    def query(self, sql_query):
        """Run a query and return the results as a Pandas Dataframe"""

        return self.bq_client.query(sql_query).to_dataframe()


def test():
    bq = GCPTool(connect_file="revelo-hebe-29868b4d02e4.json", init_list=["bigquery"])

    sql_test_query = """SELECT MAX(etl_tstamp) FROM `revelo-hebe.source_fausto.atomic_events`"""

    bq.query(sql_test_query)


if __name__ == '__main__':
    test()
