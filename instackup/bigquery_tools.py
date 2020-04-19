import os
import logging
import time
import pandas as pd
from google.cloud import bigquery
from google.cloud import bigquery_datatransfer_v1
from google.cloud.exceptions import NotFound
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

    def list_datasets(self):
        """Returns a list with all dataset names inside the project."""

        return [ds.dataset_id for ds in self.client.list_datasets()]

    def list_tables_in_dataset(self, dataset, get=None, return_type="dict"):
        """ Lists all tables inside a dataset. Will fail if dataset doesn't exist.

        get parameter can be a string or list of strings. If only a string is passed,
        will return a list of values of that attribute of all tables
        (this case overrides return_type parameter).

        return_type parameter can be 1 out of 3 types and sets how the result will be returned:
        - dict: dictionary of lists, i.e., each key has a list of all tables values for that attribute.
                The same index for different attibutes refer to the same table;
        - list: list of dictionaries, i.e., each item in the list is a dictionary with all the attributes
                of the respective table;
        - dataframe: Pandas DataFrame.
        """

        tables_list = []
        tables = {
            "clustering_fields": [],
            "created": [],
            "dataset_id": [],
            "expires": [],
            "friendly_name": [],
            "full_table_id": [],
            "labels": [],
            "partition_expiration": [],
            "partitioning_type": [],
            "project": [],
            "reference": [],
            "table_id": [],
            "table_type": [],
            "time_partitioning": [],
            "view_use_legacy_sql": [],
        }

        # Remove unwanted fields
        if get is not None:
            if type(get) is not list and type(get) is not set:
                get = {get}

            for item in get:
                if item not in tables:
                    raise ValueError(f"Item '{item}' from get field is not a valid table parameter.")

            unwanted = set(tables) - set(get)
            for unwanted_key in unwanted:
                del tables[unwanted_key]

        # DataFrame uses the same base format as dictionary return. If a single item is passed in get parameter,
        # it uses this form since returning a single list is easier using this method.
        if return_type.lower() in ["dict", "dataframe"] or len(tables) == 1:
            for table_info in self.client.list_tables(dataset):  # Will fail here if dataset doesn't exist
                for key, list_value in tables.items():
                    logger.debug("eval result = {result}".format(result=eval(f"table_info.{key}")))
                    list_value.append(eval(f"table_info.{key}"))  # Adding each parameter to its respective key list

            if return_type.lower() == "dataframe":
                logger.debug("Returning dataframe...")
                return pd.DataFrame(tables)
            else:
                if len(tables) == 1:
                    logger.debug("Only one column, returning a single list value.")
                    return tables[next(iter(tables))]
                else:
                    return tables

        elif return_type.lower() == "list":
            for table_info in self.client.list_tables(dataset):  # Will fail here if dataset doesn't exist
                for key in tables.keys():
                    tables[key] = eval(f"table_info.{key}")  # Adding each parameter to its respective key
                tables_list.append(tables)  # And appending the result to a list

            return tables_list

        else:
            raise ValueError("Invalid return type. Valid options are 'dict', 'list' or 'dataframe'.")

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

    def __job_preparation_file_upload(self, dataset, table, file_format="CSV",
                                      header_rows=1, delimiter=",", encoding="UTF-8",
                                      writing_mode="APPEND", create_table_if_needed=False, schema=None):
        """
        This is a private method used to prepare the job parameters for
        upload_from_gcs and upload_from_file methods.
        """

        # ------- Start of Job preparation -------
        job_config = bigquery.LoadJobConfig()

        table_ref = self.client.dataset(dataset).table(table)

        # Applying chosen format
        source_format = {
            "AVRO": bigquery.SourceFormat.AVRO,
            "CSV": bigquery.SourceFormat.CSV,
            "JSON": bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            "ORC": bigquery.SourceFormat.ORC,
            "PARQUET": bigquery.SourceFormat.PARQUET,
        }
        try:
            job_config.source_format = source_format[file_format.upper()]
        except ValueError:
            available_formats = list(source_format.keys())
            raise ValueError(f"Unsupported format {file_format}. Formats available: {available_formats}")

        # Applying format specific parameters
        if file_format.upper() == "CSV":
            job_config.skip_leading_rows = header_rows
            job_config.field_delimiter = delimiter
            job_config.encoding = encoding

        # Checking whether table exists and, if not and create_table_if_needed is set to False, raises an error.
        try:
            table_exists = self.client.get_table(table_ref)
            assert table_exists
        except (NotFound, AssertionError) as err:
            if create_table_if_needed:
                table_exists = None
            elif dataset not in self.list_datasets():
                logger.error("Dataset doesn't exist.")
                raise err
            else:
                logger.error("Table doesn't exist.")
                raise err

        # If table exists, sets the writing_mode
        if table_exists:
            write_disposition = {
                "APPEND": bigquery.WriteDisposition.WRITE_APPEND,
                "EMPTY": bigquery.WriteDisposition.WRITE_EMPTY,
                "TRUNCATE": bigquery.WriteDisposition.WRITE_TRUNCATE,
            }

            try:
                job_config.write_disposition = write_disposition[writing_mode.upper()]
            except ValueError:
                available_modes = list(write_disposition.keys())
                raise ValueError(f"Unsupported writing_mode {writing_mode}. Formats available: {available_modes}")

        # If table does not exist, sets the schema if given or turn on the autodetect if supported.
        else:
            if schema is None:
                if file_format.upper() in ["CSV", "JSON"]:
                    job_config.autodetect = True
                else:
                    raise ValueError("No schema given. Schema autodetection is supported only for CSV and JSON file formats.")
            else:
                job_schema = []
                if type(schema) is dict:
                    schema = schema["fields"]

                for column_info in schema:
                    if column_info.get("mode") is None:
                        column_info["mode"] = "NULLABLE"

                    logger.debug("Field parameters: name={name}, type={type}, mode={mode}, description={description}".format(
                        name=column_info["name"],
                        type=column_info["type"],
                        mode=column_info["mode"],
                        description=column_info.get("description")
                    ))

                    job_schema.append(bigquery.SchemaField(
                        column_info["name"],
                        column_info["type"],
                        mode=column_info["mode"],
                        description=column_info.get("description")
                    ))

                job_config.schema = job_schema
        # ------- End of Job preparation -------

        return job_config, table_ref

    def upload_from_gcs(self, dataset, table, gs_path, file_format="CSV",
                        header_rows=1, delimiter=",", encoding="UTF-8",
                        writing_mode="APPEND", create_table_if_needed=False, schema=None):
        """Uploads data from Google Cloud Storage directly to BigQuery.

        dataset and table parameters determines the destination of the upload.
        gs_path parameter is the file location in Google Cloud Storage.
        All 3 of them are required string parameters.

        file_format can be either 'AVRO', 'CSV', 'JSON', 'ORC' or 'PARQUET'. Defaults to 'CSV'.
        header_rows, delimiter and encoding are only used when file_format is 'CSV'.

        header_rows parameter determine the length in rows of the 'CSV' file given.
        Should be 0 if there are no headers in the file. Defaults to 1.

        delimiter determines the string character used to delimite the data. Defaults to ','.

        encoding tells the file encoding. Can be either 'UTF-8' or 'ISO-8859-1' (latin-1).
        Defaults to 'UTF-8'.

        writing_mode parameter determines how the data is going to be written in BigQuery.
        Does not apply if table doesn't exist. Can be one of 3 types (defaults in 'APPEND'):
        - APPEND: If the table already exists, BigQuery appends the data to the table.
        - EMPTY: If the table already exists and contains data, a 'duplicate' error
                 is returned in the job result.
        - TRUNCATE: If the table already exists, BigQuery overwrites the table data.

        If create_table_if_needed is set to False and the table doesn't exist, it'll raise an error.
        Dafaults to False.

        schema is either a list of dictionaries containing the schema information or
        a dictionary encapsulating the previous list with a key of 'fields'.
        This latter format can be found when directly importing the schema info from a JSON generated file.
        If the file_format is either 'CSV' or 'JSON' or the table already exists, it can be ommited.
        """

        # Setting Job configuration
        job_config, table_ref = self.__job_preparation_file_upload(
            dataset=dataset, table=table, file_format=file_format,
            header_rows=header_rows, delimiter=delimiter, encoding=encoding,
            writing_mode=writing_mode, create_table_if_needed=create_table_if_needed, schema=schema
        )

        # Job execution
        load_job = self.client.load_table_from_uri(gs_path, table_ref, job_config=job_config)  # API request

        print("Starting job {}".format(load_job.job_id))
        start_time = time.time()

        load_job.result()  # Waits for table load to complete.
        print("Job finished in {total_time:.2f} seconds.".format(total_time=time.time() - start_time))

    def upload_from_file(self, dataset, table, file_location, file_format="CSV",
                         header_rows=1, delimiter=",", encoding="UTF-8",
                         writing_mode="APPEND", create_table_if_needed=False, schema=None):
        """Uploads data from a local file to BigQuery.

        dataset and table parameters determines the destination of the upload.
        file_location parameter is either the file full or relative path in the local computer.
        All 3 of them are required string parameters.

        file_format can be either 'AVRO', 'CSV', 'JSON', 'ORC' or 'PARQUET'. Defaults to 'CSV'.
        header_rows, delimiter and encoding are only used when file_format is 'CSV'.

        header_rows parameter determine the length in rows of the 'CSV' file given.
        Should be 0 if there are no headers in the file. Defaults to 1.

        delimiter determines the string character used to delimite the data. Defaults to ','.

        encoding tells the file encoding. Can be either 'UTF-8' or 'ISO-8859-1' (latin-1).
        Defaults to 'UTF-8'.

        writing_mode parameter determines how the data is going to be written in BigQuery.
        Does not apply if table doesn't exist. Can be one of 3 types (defaults in 'APPEND'):
        - APPEND: If the table already exists, BigQuery appends the data to the table.
        - EMPTY: If the table already exists and contains data, a 'duplicate' error
                 is returned in the job result.
        - TRUNCATE: If the table already exists, BigQuery overwrites the table data.

        If create_table_if_needed is set to False and the table doesn't exist, it'll raise an error.
        Dafaults to False.

        schema is either a list of dictionaries containing the schema information or
        a dictionary encapsulating the previous list with a key of 'fields'.
        This latter format can be found when directly importing the schema info from a JSON generated file.
        If the file_format is either 'CSV' or 'JSON' or the table already exists, it can be ommited.
        """

        # Setting Job configuration
        job_config, table_ref = self.__job_preparation_file_upload(
            dataset=dataset, table=table, file_format=file_format,
            header_rows=header_rows, delimiter=delimiter, encoding=encoding,
            writing_mode=writing_mode, create_table_if_needed=create_table_if_needed, schema=schema
        )

        # Job execution
        with open(file_location, "rb") as source_file:
            load_job = self.client.load_table_from_file(source_file, table_ref, job_config=job_config)  # API request

        print("Starting job {}".format(load_job.job_id))
        start_time = time.time()

        load_job.result()  # Waits for table load to complete.
        print("Job finished in {total_time:.2f} seconds.".format(total_time=time.time() - start_time))

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
