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


# PostgreSQL reference: https://www.postgresql.org/docs/9.5/datatype.html
# BigQuery reference: https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types
POSTGRES_TO_BIGQUERY_TYPE_CONVERTER = {
    # Boolean
    "boolean": "BOOLEAN",

    # Bytes
    "bigserial": "BYTES",
    "bit": "BYTES",
    "bit varying": "BYTES",
    "bytea": "BYTES",

    # Date
    "date": "DATE",

    # Float
    "double precision": "FLOAT",
    "real": "FLOAT",

    # Integer
    "bigint": "INTEGER",
    "integer": "INTEGER",

    # Numeric
    "decimal": "NUMERIC",
    "money": "NUMERIC",
    "numeric": "NUMERIC",

    # String
    "array": "STRING",
    "character": "STRING",
    "character varying": "STRING",
    "json": "STRING",
    "jsonb": "STRING",
    "oid": "STRING",
    "text": "STRING",
    "user-defined": "STRING",
    "uuid": "STRING",

    # Time
    "time": "TIME",
    "time with time zone": "TIME",
    "time without time zone": "TIME",

    # Timestamp
    "timestamp": "TIMESTAMP",
    "timestamp with time zone": "TIMESTAMP",
    "timestamp without time zone": "TIMESTAMP",
}


# Based on this convertion table: https://miro.medium.com/max/1052/1*3lUW3r6VLR-woQv2t-sT-g.png
JSON_TO_BIGQUERY_TYPE_CONVERTER = {
    "string": "STRING",
    "number": "NUMERIC",
    "integer": "INTEGER",
    "real": "FLOAT",
    "boolean": "BOOLEAN",
    "array": "STRING",
    "object": "STRING",
    "null": "STRING",
}


class BigQueryTool(object):
    """This class handle most of the interaction needed with BigQuery,
    so the base code becomes more readable and straightforward."""

    def __init__(self, authenticate=True):
        # Code created following Google official API documentation:
        # https://cloud.google.com/bigquery/docs/reference/libraries
        # https://cloud.google.com/bigquery/docs/quickstarts/quickstart-client-libraries?hl=pt-br#bigquery_simple_app_query-python

        if authenticate:
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

    def query_and_save_results(self, sql_query, dest_dataset, dest_table, writing_mode="TRUNCATE", create_table_if_needed=False):
        """Executes a query and saves the result in a table.

        writing_mode parameter determines how the data is going to be written in BigQuery.
        Does not apply if table doesn't exist. Can be one of 3 types (defaults to 'TRUNCATE'):
        - APPEND: If the table already exists, BigQuery appends the data to the table.
        - EMPTY: If the table already exists and contains data, a 'duplicate' error
                 is returned in the job result.
        - TRUNCATE: If the table already exists, BigQuery overwrites the table data.

        If create_table_if_needed is set to False and the table doesn't exist, it'll raise an error.
        Dafaults to False.
        """

        # Job preparation
        job_config = bigquery.QueryJobConfig()

        # Setting query destination table
        table_ref = self.client.dataset(dest_dataset).table(dest_table)
        job_config.destination = table_ref

        # Checking whether table exists and, if not and create_table_if_needed is set to False, raises an error.
        try:
            table_exists = self.client.get_table(table_ref)
            assert table_exists
        except (NotFound, AssertionError) as err:
            if create_table_if_needed:
                table_exists = None
            elif dest_dataset not in self.list_datasets():
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

        # Job execution
        query_job = self.client.query(sql_query, job_config=job_config)  # API request

        print("Starting job {}".format(query_job.job_id))
        start_time = time.time()

        query_job.result()  # Waits for query and save results to complete.
        print("Job finished in {total_time:.2f} seconds.".format(total_time=time.time() - start_time))

    def list_datasets(self):
        """Returns a list with all dataset names inside the project."""

        return [ds.dataset_id for ds in self.client.list_datasets()]

    def create_dataset(self, dataset, location="US"):
        """Creates a new dataset."""

        dataset_ref = self.client.dataset(dataset)
        dataset = bigquery.Dataset(dataset_ref)

        dataset.location = location

        dataset = self.client.create_dataset(dataset)  # API request
        print("Created dataset {}".format(dataset.full_dataset_id))

    def list_tables_in_dataset(self, dataset, get=None, return_type="dict"):
        """Lists all tables inside a dataset. Will fail if dataset doesn't exist.

        get parameter can be a string or list of strings. If only a string is passed,
        will return a list of values of that attribute of all tables
        (this case overrides return_type parameter).
        Valid parameters are:
        ["clustering_fields", "created", "dataset_id", "expires", "friendly_name",
        "full_table_id", "labels", "partition_expiration", "partitioning_type", "project",
        "reference", "table_id", "table_type", "time_partitioning", "view_use_legacy_sql"]

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

    def get_table_schema(self, dataset, table):
        """Gets schema information and returns a properly formatted dictionary."""

        schema = {
            "fields": []
        }

        table_ref = self.client.dataset(dataset).table(table)
        table = self.client.get_table(table_ref)
        schema_fields = table.schema

        for schema_field in schema_fields:
            column_schema = {}

            # Required fields
            column_schema["name"] = schema_field.name
            column_schema["type"] = schema_field.field_type
            column_schema["mode"] = schema_field.mode

            # Only added if contains relevant information
            if schema_field.description is not None:
                column_schema["description"] = schema_field.description
            if len(schema_field.fields) > 0:
                column_schema["fields"] = schema_field.fields

            schema["fields"].append(column_schema)

        return schema

    def convert_postgresql_table_schema(self, dataframe, parse_json_columns=True):
        """Receives a dataframe containing schema information from exactly one table from PostgreSQL db
        and converts it to a BigQuery schema format that can be used to upload data.

        If parse_json_columns is set to False, it'll ignore json and jsonb fields, setting them as STRING.
        If it is set to True, it'll look for json and jsonb keys and value types in json_key and json_value_type
        columns, respectively, in the dataframe. If those columns does not exist, this method will fail.

        Returns a dictionary containing the BigQuery formatted schema.
        """

        # Since some operations might change the DataFrame, it starts by making a copy of the parameter given
        df = dataframe.copy()

        # Basic check to see if the given DataFrame is compliant with the method's needs
        if parse_json_columns and ('json' in df['data_type'].values or 'jsonb' in df['data_type'].values):
            try:
                assert set(['json_key', 'json_value_type']).issubset(df.columns.values.tolist())
            except AssertionError:
                raise ValueError("'json_key' and 'json_value_type' are not part of given DataFrame.")
        else:
            try:
                df = df[df["json_key"] != ""]
                df.drop(['json_key', 'json_value_type'], axis=1, inplace=True)
            except KeyError:
                pass

        schema = {
            "fields": []
        }

        for index, row in df.iterrows():
            column_name = row['column_name']
            data_type = row['data_type']
            required = row.get("is_nullable")

            # Getting proper column type from dict reference
            try:
                column_type = POSTGRES_TO_BIGQUERY_TYPE_CONVERTER[data_type.lower()]
            except KeyError:
                column_type = "STRING"

            # Setting proper column mode
            if data_type.lower() == "array":
                mode = "REPEATED"
            else:
                if required:
                    mode = "REQUIRED"
                else:
                    mode = "NULLABLE"

            if parse_json_columns and data_type.lower() in ['jsonb', 'json']:

                # Checks whether this column was already added to the schema or not
                if column_name not in [x['name'] for x in schema['fields']]:

                    # Filters the DataFrame so just the rows where there are relevant
                    # information about the focused json keys-values column are being searched
                    json_col_df = df[(df['column_name'] == column_name) & (df['json_key'] != "")]

                    fields = []
                    for _, json_row in json_col_df.iterrows():
                        json_key = json_row['json_key']
                        json_value_type = json_row['json_value_type']

                        # Getting proper column type from dict reference
                        try:
                            json_value_column_type = JSON_TO_BIGQUERY_TYPE_CONVERTER[json_value_type.lower()]
                        except KeyError:
                            json_value_column_type = "STRING"

                        # If type is an Array, sets the right mode value
                        if json_value_type.lower() == "array":
                            json_value_mode = "REPEATED"
                        else:
                            json_value_mode = "NULLABLE"

                        # Add converted json key data type to the fields list
                        fields.append({
                            "type": json_value_column_type,
                            "name": json_key,
                            "mode": json_value_mode
                        })

                    # Adding converted column metadata to list
                    column_schema = {
                        "type": "RECORD",
                        "name": column_name,
                        "mode": "REPEATED",
                        "fields": fields
                    }
                    schema['fields'].append(column_schema)

            else:
                # Adding converted column metadata to list
                column_schema = {
                    "type": column_type,
                    "name": column_name,
                    "mode": mode
                }
                schema['fields'].append(column_schema)

        # Sorting field list by names.
        # Idea from https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-a-value-of-the-dictionary
        schema["fields"] = sorted(schema["fields"], key=lambda k: k['name'])

        return schema

    def convert_multiple_postgresql_tables_schema(self, dataframe, parse_json_columns=True):
        """Receives a dataframe containing schema information from exactly one or more tables from PostgreSQL db
        and converts it to a BigQuery schema format that can be used to upload data.

        If parse_json_columns is set to False, it'll ignore json and jsonb fields, setting them as STRING.
        If it is set to True, it'll look for json and jsonb keys and value types in json_key and json_value_type
        columns, respectively, in the dataframe. If those columns does not exist, this method will fail.

        Returns a dictionary containing the table "full name" and the BigQuery formatted schema as key-value pairs.
        """

        dataframe['table_ref'] = dataframe[['table_catalog', 'table_schema', 'table_name']].agg('-'.join, axis=1)

        schema_collection = {}
        for table_ref in set(dataframe['table_ref'].to_list()):
            schema_collection[table_ref] = self.convert_postgresql_table_schema(dataframe[dataframe['table_ref'] == table_ref], parse_json_columns=parse_json_columns)

        return schema_collection

    def convert_dataframe_to_numeric(self, dataframe, exclude_columns=[], **kwargs):
        """Transform all string type columns into floats, except those in exclude_columns list.

        **kwargs are passed directly to pandas.to_numeric method.
        The complete documentation of this method can be found here:
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_numeric.html
        """
        object_cols = dataframe.columns[dataframe.dtypes.eq('object')]
        cols = [x for x in object_cols if x not in exclude_columns]
        dataframe[cols] = dataframe[cols].apply(pd.to_numeric, **kwargs)
        return dataframe

    def clean_dataframe_column_names(self, dataframe, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789", special_treatment={}):
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

    def __parse_schema(self, schema):
        """This is a private method used to parse a json formatted schema into a Python specific
        BigQuery API format for the (also private) __job_preparation_file_upload method.
        """

        job_schema = []

        if type(schema) is dict:
            schema = schema["fields"]

        for column_info in schema:
            if column_info.get("mode") is None:
                column_info["mode"] = "NULLABLE"

            try:
                assert column_info["name"]
                assert column_info["type"]
            except KeyError:
                raise ValueError("Field incomplete. Doesn't have name and/or type parameters.")

            logger.debug("Field parameters: name={name}, type={type}, mode={mode}, description={description}".format(
                name=column_info["name"],
                type=column_info["type"],
                mode=column_info["mode"],
                description=column_info.get("description")
            ))

            if column_info["type"].upper() == "RECORD":
                fields = []
                try:
                    assert len(column_info["fields"]) > 0
                except (AssertionError, KeyError):
                    raise ValueError("Field {name} has RECORD type, but no associated nested fields".format(name=column_info["name"]))
                else:
                    fields = tuple(self.__parse_schema(schema=column_info["fields"]))
            else:
                fields = tuple()

            job_schema.append(bigquery.SchemaField(
                column_info["name"],
                column_info["type"],
                mode=column_info["mode"],
                description=column_info.get("description"),
                fields=fields
            ))

        return job_schema

    def create_empty_table(self, dataset, table, schema):
        """Creates an empty table at dataset.table location, based on schema given"""

        schema = self.__parse_schema(schema=schema)

        table_ref = self.dataset(dataset).table(table)
        table = bigquery.Table(table_ref, schema=schema)

        table = self.client.create_table(table)  # API request
        print("Created table {}".format(table.full_table_id))

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
                job_config.schema = self.__parse_schema(schema=schema)
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
        Does not apply if table doesn't exist. Can be one of 3 types (defaults to 'APPEND'):
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
        Does not apply if table doesn't exist. Can be one of 3 types (defaults to 'APPEND'):
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
