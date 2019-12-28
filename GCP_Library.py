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


def test():
    bq = GCPTool(connect_file="revelo-hebe-29868b4d02e4.json", init_list=["bigquery"])

    sql_test_query = """SELECT MAX(etl_tstamp) FROM `revelo-hebe.source_fausto.atomic_events`"""

    df = bq.query(sql_test_query)
    print(df)


if __name__ == '__main__':
    test()
