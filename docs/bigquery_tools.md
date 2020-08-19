# bigquery_tools
This is the documentation for the bigquery_tools module and all its contents, with usage examples.

# Index
- [Global Variables](#global-variables)
- [BigQueryTool](#bigquerytool)
  - [\_\_init\_\_(self, authenticate=True)](#__init__self-authenticatetrue)
  - [query(self, sql_query)](#queryself-sql_query)
  - [query_and_save_results(self, sql_query, dest_dataset, dest_table, writing_mode="TRUNCATE", create_table_if_needed=False)](#query_and_save_resultsself-sql_query-dest_dataset-dest_table-writing_modetruncate-create_table_if_neededfalse)
  - [list_datasets(self)](#list_datasetsself)
  - [create_dataset(self, dataset, location="US")](#create_datasetself-dataset-locationus)
  - [list_tables_in_dataset(self, dataset, get=None, return_type="dict")](#list_tables_in_datasetself-dataset-getnone-return_typedict)
  - [get_table_schema(self, dataset, table)](#get_table_schemaself-dataset-table)
  - [convert_postgresql_table_schema(self, dataframe, parse_json_columns=True)](#convert_postgresql_table_schemaself-dataframe-parse_json_columnstrue)
  - [convert_multiple_postgresql_tables_schema(self, dataframe, parse_json_columns=True)](#convert_multiple_postgresql_tables_schemaself-dataframe-parse_json_columnstrue)
  - [convert_dataframe_to_numeric(dataframe, exclude_columns=[], \*\*kwargs)](#convert_dataframe_to_numericdataframe-exclude_columns-kwargs)
  - [clean_dataframe_column_names(dataframe, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789", special_treatment={})](#clean_dataframe_column_namesdataframe-allowed_charsabcdefghijklmnopqrstuvwxyz0123456789-special_treatment)
  - [upload(self, dataframe, dataset, table, \*\*kwargs)](#uploadself-dataframe-dataset-table-kwargs)
  - [create_empty_table(self, dataset, table, schema)](#create_empty_tableself-dataset-table-schema)
  - [upload_from_gcs(self, dataset, table, gs_path, file_format="CSV", header_rows=1, delimiter=",", encoding="UTF-8", ignore_unknown_values=False, max_bad_records=0, writing_mode="APPEND", create_table_if_needed=False, schema=None)](#upload_from_gcsself-dataset-table-gs_path-file_formatcsv-header_rows1-delimiter-encodingutf-8-ignore_unknown_valuesfalse-max_bad_records0-writing_modeappend-create_table_if_neededfalse-schemanone)
  - [upload_from_file(self, dataset, table, file_location, file_format="CSV", header_rows=1, delimiter=",", encoding="UTF-8", ignore_unknown_values=False, max_bad_records=0, writing_mode="APPEND", create_table_if_needed=False, schema=None)](#upload_from_fileself-dataset-table-file_location-file_formatcsv-header_rows1-delimiter-encodingutf-8-ignore_unknown_valuesfalse-max_bad_records0-writing_modeappend-create_table_if_neededfalse-schemanone)
  - [start_transfer(self, project_path=None, project_name=None, transfer_name=None)](#start_transferself-project_pathnone-project_namenone-transfer_namenone)

# Module Contents
## Global Variables
There are some global variables that can be accessed an edited by the user. Those are:
- **POSTGRES_TO_BIGQUERY_TYPE_CONVERTER**: Dictionary that is used to convert the column types from PostgreSQL to BigQuery Standard SQL.
- **JSON_TO_BIGQUERY_TYPE_CONVERTER**: Dictionary that is used to convert the column types from JSON fields into BigQuery Standard SQL.

## BigQueryTool
This class handle most of the interaction needed with BigQuery, so the base code becomes more readable and straightforward.

### \_\_init\_\_(self, authenticate=True)
The initialization process sets the bigquery client.

The _authenticate_ parameter sets whether the initialization process will use the `fetch_credentials` function or not. This might be desired if the environment is already authenticated, for example in a Google Cloud Composer environment.

Usage example:
```
from instackup.bigquery_tools import BigQueryTool


bq = BigQueryTool()
```

### query(self, sql_query)
Run a SQL query and return the results as a Pandas Dataframe.

Usage example:
```
import pandas as pd
from instackup.bigquery_tools import BigQueryTool


bq = BigQueryTool()

sql_query = """SELECT * FROM `project_name.dataset.table`"""
df = bq.query(sql_query)
```

### query_and_save_results(self, sql_query, dest_dataset, dest_table, writing_mode="TRUNCATE", create_table_if_needed=False)
Executes a query and saves the result in a table. It has no return value.

_writing_mode_ parameter determines how the data is going to be written in BigQuery.
Does not apply if table doesn't exist. Can be one of 3 types (defaults to 'TRUNCATE'):
- APPEND: If the table already exists, BigQuery appends the data to the table.
- EMPTY: If the table already exists and contains data, a 'duplicate' error
         is returned in the job result.
- TRUNCATE: If the table already exists, BigQuery overwrites the table data.

If _create_table_if_needed_ is set to False and the table doesn't exist, it'll raise an error. Defaults to False.

Usage example:
```
from instackup.bigquery_tools import BigQueryTool


# Enter valid values here
dest_dataset = "dataset"
dest_table = "some_other_table"
sql_query = """SELECT * FROM `project_name.dataset.table`"""

bq = BigQueryTool()

bq.query_and_save_results(self, sql_query, dest_dataset, dest_table, create_table_if_needed=True)
```

### list_datasets(self)
Returns a list with all dataset names inside the project.

Usage example:
```
from instackup.bigquery_tools import BigQueryTool


bq = BigQueryTool()

datasets = bq.list_datasets()

print("There are {num} datasets, which are listed bellow:\n".format(num=len(datasets)))
for ds in datasets:
    print(ds)
```

### create_dataset(self, dataset, location="US")
Creates a new dataset.

Usage example:
```
from instackup.bigquery_tools import BigQueryTool


bq = BigQueryTool()

datasets = bq.create_dataset("google_analytics_reports")
```

### list_tables_in_dataset(self, dataset, get=None, return_type="dict")
Lists all tables inside a dataset. Will fail if dataset doesn't exist.

_get_ parameter can be a string or list of strings. If only a string is passed,
will return a list of values of that attribute of all tables
(this case overrides return_type parameter).

Valid _get_ parameters are:
["clustering_fields", "created", "dataset_id", "expires", "friendly_name",
"full_table_id", "labels", "partition_expiration", "partitioning_type", "project",
"reference", "table_id", "table_type", "time_partitioning", "view_use_legacy_sql"]

_return_type_ parameter can be 1 out of 3 types and sets how the result will be returned:
- dict: dictionary of lists, i.e., each key has a list of all tables values for that attribute.
        The same index for different attibutes refer to the same table;
- list: list of dictionaries, i.e., each item in the list is a dictionary with all the attributes
        of the respective table;
- dataframe: Pandas DataFrame.

Usage example:
```
from instackup.bigquery_tools import BigQueryTool


bq = BigQueryTool()

dataset = "dataset"  # Enter a valid dataset name

tables = bq.list_tables_in_dataset(dataset, get="table_id")  # Getting only table name

print("There are {num} tables in {ds}, which are listed bellow:\n".format(num=len(tables), ds=dataset))
for tb in tables:
    print(tb)

# Getting all table info
df = bq.list_tables_in_dataset(dataset, return_type="dataframe")
print(df)
```

### get_table_schema(self, dataset, table)
Gets schema information from the given _dataset_ and _table_ and returns a properly formatted dictionary.

Usage example:
```
import json
from instackup.bigquery_tools import BigQueryTool


bq = BigQueryTool()

dataset = "dataset"  # Enter a valid dataset name
table = "table"      # Enter a valid table name

schema = bq.get_table_schema(dataset, table)

with open('data.json', 'w') as fp:
    json.dump(schema, fp, sort_keys=True, indent=4)
```

### convert_postgresql_table_schema(self, dataframe, parse_json_columns=True)
Receives a Pandas DataFrame containing schema information from exactly one table from PostgreSQL db and converts it to a BigQuery schema format that can be used to upload data.

If _parse_json_columns_ is set to False, it'll ignore json and jsonb fields, setting them as STRING.

If it is set to True, it'll look for json and jsonb keys and value types in json_key and json_value_type columns, respectively, in the DataFrame. If those columns does not exist, this method will fail.

Returns a dictionary containing the BigQuery formatted schema.

Usage example:
```
import json
from instackup.bigquery_tools import BigQueryTool
from instackup.postgresql_tools import PostgreSQLTool


# Getting the PostgreSQL schema
with PostgreSQLTool(connection="prod_db") as pg:
  df = pg.describe_table()

# Converting the schema from PostgreSQL format to BigQuery format
bq = BigQueryTool()
schema = bq.convert_postgresql_table_schema(df)

# Saving schema
with open('data.json', 'w') as fp:
    json.dump(schema, fp, sort_keys=True, indent=4)
```

### convert_multiple_postgresql_tables_schema(self, dataframe, parse_json_columns=True)
Receives a Pandas DataFrame containing schema information from one or more tables from PostgreSQL db and converts it to a BigQuery schema format that can be used to upload data.

If _parse_json_columns_ is set to False, it'll ignore json and jsonb fields, setting them as STRING.

If it is set to True, it'll look for json and jsonb keys and value types in json_key and json_value_type columns, respectively, in the DataFrame. If those columns does not exist, this method will fail.

Returns a dictionary containing the table "full name" and its respective BigQuery formatted schema as key-value pairs.

Usage example:
```
import os
import json
from instackup.bigquery_tools import BigQueryTool
from instackup.postgresql_tools import PostgreSQLTool


# Getting the PostgreSQL schema from all tables in the DB
with PostgreSQLTool(connection="prod_db") as pg:
  df = pg.get_all_db_info()

# Converting all the schemas from PostgreSQL format to BigQuery format
bq = BigQueryTool()
schemas = bq.convert_multiple_postgresql_tables_schema(df)

# Saving schemas
os.makedirs(os.getcwd(), "schemas")
for name, schema in schemas.items():
    with open(os.path.join('schemas', f'{name}.json'), 'w') as fp:
        json.dump(schema, fp, sort_keys=True, indent=4)
```

### convert_dataframe_to_numeric(dataframe, exclude_columns=[], \*\*kwargs)
Transform all string type columns into floats, except those in _exclude_columns_ list.

_\*\*kwargs_ are passed directly to _pandas.to_numeric_ method.
The complete documentation of this method can be found here:
https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_numeric.html

Usage example:
```
import pandas as pd
from instackup.bigquery_tools import BigQueryTool


# You can often find these kind of data when reading from a file
df = pd.DataFrame({"col.1": ["1", "2"], "col.2": ["3", "junk"], "col.3": ["string1", "string2"]})

bq = BigQueryTool()
df = bq.convert_dataframe_to_numeric(df, exclude_columns=["col.3"], errors="coerce")
print(df)

# output:
#
#    col.1  col.2    col.3
# 0      1    3.0  string1
# 1      2    NaN  string2
```

### clean_dataframe_column_names(dataframe, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789", special_treatment={})
Replace _dataframe_ column names to only contain chars allowed in BigQuery tables column name.

_special_treatment_ dictionary substitutes the terms in the keys by its value pair.

If a character is not in _allowed_chars_ string parameter, neither in a key from the _special_treatment_ dictionary, it'll be replaced by an underscore (\_).

Usage example:
```
import pandas as pd
from instackup.bigquery_tools import BigQueryTool


# You can often find these kind of data when reading from a file
df = pd.DataFrame({"col.1": ["1", "2"], "col.2": ["3", "junk"], "col.3!": ["string1", "string2"]})

bq = BigQueryTool()
df = bq.clean_dataframe_column_names(df, special_treatment={"!": "_factorial"})
print(df)

# output:
#
#   col_1 col_2 col_3_factorial
# 0     1     3         string1
# 1     2  junk         string2
```

### upload(self, dataframe, dataset, table, \*\*kwargs)
Clean the dataframe column names and executes a command equivalent of SQL "INSERT" into BigQuery.

_\*\*kwargs_ are passed directly to pandas.to_gbq method.
The complete documentation of this method can be found here:
https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_gbq.html

Usage example:
```
import pandas as pd
from instackup.bigquery_tools import BigQueryTool


fixed_data = {
  'col1': [1, 2],
  'col2': [0.5, 0.75]
}

df = pd.DataFrame(fixed_data)

dataset = "some_dataset_name"
table = "some_table_name"

bq = BigQueryTool()
bq.upload(df, dataset, table)
```

### create_empty_table(self, dataset, table, schema)
Creates an empty table at _dataset_._table_ location, based on _schema_ given.

Usage example:
```
from instackup.bigquery_tools import BigQueryTool


schema = {
    'fields': [
        {
            "type": "INTEGER",
            "name": "id",
            "mode": "NULLABLE"
        },
        {
            "type": "STRING",
            "name": "name",
            "mode": "NULLABLE"
        }
    ]
}

dataset = "some_dataset_name"
table = "some_table_name"

bq = BigQueryTool()
bq.create_empty_table(dataset, table, schema)
```

### upload_from_gcs(self, dataset, table, gs_path, file_format="CSV", header_rows=1, delimiter=",", encoding="UTF-8", ignore_unknown_values=False, max_bad_records=0, writing_mode="APPEND", create_table_if_needed=False, schema=None)
Uploads data from Google Cloud Storage directly to BigQuery.

_dataset_ and _table_ parameters determines the destination of the upload.
_gs_path_ parameter is the file location in Google Cloud Storage.
All 3 of them are required string parameters.

_file_format_ can be either 'AVRO', 'CSV', 'JSON', 'ORC' or 'PARQUET'. Defaults to 'CSV'.
_header_rows_, _delimiter_ and _encoding_ are only used when _file_format_ is 'CSV'.

_header_rows_ parameter determine the length in rows of the CSV header in the file given.
Should be 0 if there are no headers in the file. Defaults to 1.

_delimiter_ determines the string character used to delimite the data. Defaults to ','.

_encoding_ tells the file encoding. Can be either 'UTF-8' or 'ISO-8859-1' (latin-1). Defaults to 'UTF-8'.

_ignore_unknown_values_ indicates if it should allow extra values that are not represented in the table schema. If True, the extra values are ignored. If False, records with extra columns are treated as bad records. Defaults to False.

_max_bad_records_ is the maximum number of bad records allowed; if it exceeds this value, it'll raise an error. Defaults to 0 (i.e. all values must be valid).

_writing_mode_ parameter determines how the data is going to be written in BigQuery.
Does not apply if table doesn't exist. Can be 1 out of 3 types (defaults in 'APPEND'):
- APPEND: If the table already exists, BigQuery appends the data to the table.
- EMPTY: If the table already exists and contains data, a 'duplicate' error
         is returned in the job result.
- TRUNCATE: If the table already exists, BigQuery overwrites the table data.

If _create_table_if_needed_ is set to False and the table doesn't exist, it'll raise an error. Dafaults to False.

_schema_ is either a list of dictionaries containing the schema information or a dictionary encapsulating the previous list with a key of 'fields'. This latter format can be found when directly importing the schema info from a JSON generated file. If the file_format is either 'CSV' or 'JSON' or the table already exists, this parameter can be ommited.

Usage example:
```
import json
from instackup.bigquery_tools import BigQueryTool


# Enter valid values here
dataset = "sandbox"
table = "test"
gs_path = "gs://some-bucket/some-subfolder/test.json"

# schema must be in the same format of the output of get_table_schema method.
with open('data.json', 'r') as fp:
    schema = json.load(fp)

bq.upload_from_gcs(dataset, table, gs_path, file_format="JSON", create_table_if_needed=True, schema=schema)
```

### upload_from_file(self, dataset, table, file_location, file_format="CSV", header_rows=1, delimiter=",", encoding="UTF-8", ignore_unknown_values=False, max_bad_records=0, writing_mode="APPEND", create_table_if_needed=False, schema=None)
Uploads data from a local file to BigQuery.

_dataset_ and _table_ parameters determines the destination of the upload.
_file_location_ parameter is either the file full or relative path in the local computer.
All 3 of them are required string parameters.

_file_format_ can be either 'AVRO', 'CSV', 'JSON', 'ORC' or 'PARQUET'. Defaults to 'CSV'.
_header_rows_, _delimiter_ and _encoding_ are only used when _file_format_ is 'CSV'.

_header_rows_ parameter determine the length in rows of the CSV header in the file given.
Should be 0 if there are no headers in the file. Defaults to 1.

_delimiter_ determines the string character used to delimite the data. Defaults to ','.

_encoding_ tells the file encoding. Can be either 'UTF-8' or 'ISO-8859-1' (latin-1). Defaults to 'UTF-8'.

_ignore_unknown_values_ indicates if it should allow extra values that are not represented in the table schema. If True, the extra values are ignored. If False, records with extra columns are treated as bad records. Defaults to False.

_max_bad_records_ is the maximum number of bad records allowed; if it exceeds this value, it'll raise an error. Defaults to 0 (i.e. all values must be valid).

_writing_mode_ parameter determines how the data is going to be written in BigQuery.
Does not apply if table doesn't exist. Can be 1 out of 3 types (defaults in 'APPEND'):
- APPEND: If the table already exists, BigQuery appends the data to the table.
- EMPTY: If the table already exists and contains data, a 'duplicate' error
         is returned in the job result.
- TRUNCATE: If the table already exists, BigQuery overwrites the table data.

If _create_table_if_needed_ is set to False and the table doesn't exist, it'll raise an error. Dafaults to False.

_schema_ is either a list of dictionaries containing the schema information or a dictionary encapsulating the previous list with a key of 'fields'. This latter format can be found when directly importing the schema info from a JSON generated file. If the file_format is either 'CSV' or 'JSON' or the table already exists, this parameter can be ommited.

Usage example:
```
import json
from instackup.bigquery_tools import BigQueryTool


# Enter valid values here
dataset = "sandbox"
table = "test"
file_location = "test.csv"

# schema must be in the same format of the output of get_table_schema method.
with open('data.json', 'r') as fp:
    schema = json.load(fp)

bq.upload_from_file(dataset, table, file_location, create_table_if_needed=True, schema=schema)
```

### start_transfer(self, project_path=None, project_name=None, transfer_name=None)
Takes a project path or both project name and transfer name to trigger a transfer to start executing in BigQuery Transfer. Returns a status indicating if the request was processed (if it does, the response should be 'PENDING').

API documentation: https://googleapis.dev/python/bigquerydatatransfer/latest/gapic/v1/api.html

Usage example:
```
from instackup.bigquery_tools import BigQueryTool


transfer_config = "projects/000000000000/transferConfigs/00000000-0000-0000-0000-000000000000"

use_project_path = True
print("Starting transfer...")

# Both options do the same thing
if use_project_path:
    state_response = bq.start_transfer(project_path=transfer_config)
else:
    state_response = bq.start_transfer(project_name="project_name", transfer_name="transfer_name")

print(f"Transfer status: {state_response}")
```
