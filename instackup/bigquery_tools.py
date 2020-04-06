import os
import logging
import pandas as pd
from google.cloud import bigquery
from google.cloud import bigquery_datatransfer_v1
from google.protobuf.timestamp_pb2 import Timestamp
from .general_tools import fetch_credentials, unicode_to_ascii


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "bigquery_tools.log"))
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

    def convert_dataframe_to_numeric(dataframe, exclude_columns=[], **kwargs):
        """Transform all string type columns into floats, except those in exclude_columns list.

        **kwargs are passed directly to pandas.to_numeric method.
        The complete documentation of this method can be found here:
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_numeric.html
        """
        object_cols = dataframe.columns[dataframe.dtypes.eq('object')]
        cols = [x for x in object_cols if x not in exclude_columns]
        dataframe[cols] = dataframe[cols].apply(pd.to_numeric, **kwargs)
        return dataframe

    def clean_dataframe_column_names(dataframe, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789", special_treatment={}):
        """Replace dataframe columns to only contain chars allowed in BigQuery tables column name.
        special_treatment dictionary substitutes the terms in the keys by its value pair.
        """

        column_map = {}
        for raw_data in dataframe.columns:
            ascii_data = unicode_to_ascii(raw_data.lower())
            clean_data = "".join([x if x in allowed_chars else "_" if special_treatment.get(x) is None else special_treatment[x] for x in ascii_data])

            # Column can't start with a number
            if clean_data[0] in "0123456789":
                clean_data = "_" + clean_data
            column_map[raw_data] = clean_data

        logger.debug(f"column_map = {column_map}")
        return dataframe.rename(column_map, axis=1)

    def upload(self, dataframe, dataset, table, **kwargs):
        """Prepare dataframe columns and executes an insert SQL command into BigQuery

        **kwargs are passed directly to pandas.to_gbq method.
        The complete documentation of this method can be found here:
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_gbq.html
        """

        dataframe = self.clean_dataframe_column_names(dataframe)

        logger.info("Starting upload...")
        destination = dataset + "." + table
        dataframe.to_gbq(destination, **kwargs)

    def start_transfer(self, project_path=None, project_name=None, transfer_name=None):
        """Trigger a transfer to start executing in BigQuery Transfer.
        API documentation: https://googleapis.dev/python/bigquerydatatransfer/latest/gapic/v1/api.html
        """

        # Getting dictionary of project names and ids.
        project_ids = fetch_credentials("BigQuery", dictionary="project_id")

        # Initiating client
        if self.transfer_client is None:
            self.transfer_client = bigquery_datatransfer_v1.DataTransferServiceClient()

        # If project_path is given with other parameter, it will ignore the others and continue with
        # project_path given.
        if project_path is None:
            # If one of the arguments is missing, this method fails
            if project_name is None or transfer_name is None:
                logger.exception("Specify either project and transfer names or transferConfig project path.")
                raise ValueError("Specify either project and transfer names or transferConfig project path.")

            else:
                # Get project id from dictionary
                try:
                    project_id = project_ids[project_name]
                except KeyError:
                    logger.exception("Project name not found in secrets file. Please add in secrets file or use the project_path parameter instead.")
                    raise KeyError("Project name not found in secrets file. Please add in secrets file or use the project_path parameter instead.")

                # Setting parent project path
                parent = self.transfer_client.project_path(project_id)

                # Listing all transfers and retrieving transfer_id from match with transfer display_name
                for element in self.transfer_client.list_transfer_configs(parent):
                    if element.display_name == transfer_name:
                        transfer_id = element.name.split("/")[-1]
                        break

                # Setting project path. If there was no match for transfer, this method fails
                try:
                    project_path = self.transfer_client.project_transfer_config_path(project_id, transfer_id)
                except NameError:
                    logger.exception("No transfer with display name given was found.")
                    raise NameError("No transfer with display name given was found.")

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
