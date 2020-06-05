# Instackup
This Python library is an open source way to standardize and simplify connections with cloud-based tools and databases and commonly used tools in data manipulation and analysis.

# Index

- [Current release](#current-release)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Documentation](#documentation)
  - [bigquery_tools](#bigquery_tools)
  - [gcloudstorage_tools](#gcloudstorage_tools)
  - [general_tools](#general_tools)
  - [heroku_tools](#heroku_tools)
  - [postgresql_tools](#postgresql_tools)
  - [redshift_tools](#redshift_tools)
  - [s3_tools](#s3_tools)
- [Version log](#version-log)

# Current release
## Version 0.0.5 (alpha)
Fifth alpha release.

#### Added modules:
- heroku_tools
- postgresql_tools

Inside those modules, these classes and functions/methods were added:
- HerokuTool
  - \_\_init\_\_
  - app_flag @property
  - execute
- PostgreSQLTool
  - \_\_init\_\_
  - connect
  - commit
  - rollback
  - execute_sql
  - query
  - unload_to_S3
  - close_connection
  - \_\_enter\_\_
  - \_\_exit\_\_

#### New functionalities:
- bigquery_tools
  - BigQueryTool
    - convert_postgresql_table_schema
    - convert_multiple_postgresql_tables_schema

#### Modified functionalities:
- general_tools
  - fetch_credentials

#### Bug fixes:
- BigQueryTool.convert_dataframe_to_numeric and BigQueryTool.clean_dataframe_column_names methods were failing because the self parameter was missing.

#### Functionalities still in development:
- gcloudstorage_tools
  - GCloudStorageTool
    - rename_file
    - rename_subfolder
    - upload_subfolder
    - download_subfolder
    - delete_file
    - delete_subfolder
- s3_tools
  - S3Tool
    - upload_subfolder
    - download_subfolder

# Prerequisites
1. Have a [Python 3.6 version or superior](https://www.python.org/downloads/) installed;
2. Create a YAML (or JSON) file with credentials information;
3. [Optional but recommended] Configure an Environment Variable that points where the Credentials file is.

### 1. Have a Python 3.6 version or superior installed
Got to this [link](https://www.python.org/downloads/) e download the most current version that is compatible with this package.

### 2. Create a YAML (or JSON) file with credentials information

Use the files [secret_template.yml](https://github.com/Lavedonio/instackup/blob/master/credentials/secret_template.yml) or [secret_blank.yml](https://github.com/Lavedonio/instackup/blob/master/credentials/secret_blank.yml) as a base or copy and paste the code bellow and modify its values to the ones in your credentials/projects:

```
#################################################################
#                                                               #
#        ACCOUNTS CREDENTIALS. DO NOT SHARE THIS FILE.          #
#                                                               #
# Specifications:                                               #
# - For the credentials you don't have, leave it blank.         #
# - Keep Google's secret file in the same folder as this file.  #
# - BigQuery project_ids must be strings, i.e., inside quotes.  #
#                                                               #
# Recommendations:                                              #
# - YAML specification: https://yaml.org/spec/1.2/spec.html     #
# - Keep this file in a static path like a folder within the    #
# Desktop. Ex.: C:\Users\USER\Desktop\Credentials\secret.yml    #
#                                                               #
#################################################################


Google:
  secret_filename: file.json

BigQuery:
  project_id:
    project_name: "000000000000"

AWS:
  access_key: AWSAWSAWSAWSAWSAWSAWS
  secret_key: CcasldUYkfsadcSDadskfDSDAsdUYalf

RedShift:
  cluster_credentials:
    dbname: db
    user: masteruser
    host: blablabla.random.us-east-2.redshift.amazonaws.com
    cluster_id: cluster
    port: 5439
  master_password:
    dbname: db
    user: masteruser
    host: blablabla.random.us-east-2.redshift.amazonaws.com
    password: masterpassword
    port: 5439

PostgreSQL:
  default:
    dbname: postgres
    user: postgres
    host: localhost
    password:
    port: 5432
```
Save this file with `.yml` extension in a folder where you know the path won't be modified, like the Desktop folder (Example: `C:\Users\USER\Desktop\Credentials\secret.yml`).

If you prefer, you can follow this step using a JSON file instead. Follow the same instructions but using `.json` instead of `.yml`.

### 3. [Optional but recommended] Configure an Environment Variable that points where the Credentials file is.

To configure the Environment Variable, follow the instructions bellow, based on your Operating System.

#### Windows
1. Place the YAML (or JSON) file in a folder you won't change its name or path later;
2. In Windows Search, type `Environment Variables` and click in the Control Panel result;
3. Click on the button `Environment Variables...`;
4. In **Environment Variables**, click on the button `New`;
5. In **Variable name** type `CREDENTIALS_HOME` and in **Variable value** paste the full path to the recently created YAML (or JSON) file;
6. Click **Ok** in the 3 open windows.

#### Linux/MacOS
1. Place the YAML (or JSON) file in a folder you won't change its name or path later;
2. Open the file `.bashrc`. If it doesn't exists, create one in the `HOME` directory. If you don't know how to get there, open the Terminal, type `cd` and then **ENTER**;
3. Inside the file, in a new line, type the command: `export CREDENTIALS_HOME="/path/to/file"`, replacing the content inside quotes by the full path to the recently created YAML (or JSON) file;
4. Save the file and restart all open Terminal windows.

> **Note:** If you don't follow this last prerequisite, you need to set the environment variable manually inside the code. To do that, inside your python code, after the imports, type the command (replacing the content inside quotes by the full path to the recently created YAML (or JSON) file):

```
os.environ["CREDENTIALS_HOME"] = "/path/to/file"
```

# Installation
Go to the Terminal and type:

    pip install instackup

# Documentation
## bigquery_tools
### BigQueryTool
This class handle most of the interaction needed with BigQuery, so the base code becomes more readable and straightforward.

#### \_\_init\_\_(self)
Initialization takes no parameter and has no return value. It sets the bigquery client.

Usage example:
```
from instackup.bigquery_tools import BigQueryTool


bq = BigQueryTool()
```

#### query(self, sql_query)
Run a SQL query and return the results as a Pandas Dataframe.

Usage example:
```
import pandas as pd
from instackup.bigquery_tools import BigQueryTool


bq = BigQueryTool()

sql_query = """SELECT * FROM `project_name.dataset.table`"""
df = bq.query(sql_query)
```

#### query_and_save_results(self, sql_query, dest_dataset, dest_table, writing_mode="TRUNCATE", create_table_if_needed=False)
Executes a query and saves the result in a table.

writing_mode parameter determines how the data is going to be written in BigQuery.
Does not apply if table doesn't exist. Can be one of 3 types (defaults to 'TRUNCATE'):
- APPEND: If the table already exists, BigQuery appends the data to the table.
- EMPTY: If the table already exists and contains data, a 'duplicate' error
         is returned in the job result.
- TRUNCATE: If the table already exists, BigQuery overwrites the table data.

If create_table_if_needed is set to False and the table doesn't exist, it'll raise an error.
Dafaults to False.

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

#### list_datasets(self)
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

#### list_tables_in_dataset(self, dataset, get=None, return_type="dict")
Lists all tables inside a dataset. Will fail if dataset doesn't exist.

get parameter can be a string or list of strings. If only a string is passed,
will return a list of values of that attribute of all tables
(this case overrides return_type parameter).

Valid get parameters are:
["clustering_fields", "created", "dataset_id", "expires", "friendly_name",
"full_table_id", "labels", "partition_expiration", "partitioning_type", "project",
"reference", "table_id", "table_type", "time_partitioning", "view_use_legacy_sql"]

return_type parameter can be 1 out of 3 types and sets how the result will be returned:
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

#### get_table_schema(self, dataset, table)
Gets schema information and returns a properly formatted dictionary.

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

#### convert_dataframe_to_numeric(dataframe, exclude_columns=[], \*\*kwargs)
Transform all string type columns into floats, except those in exclude_columns list.

\*\*kwargs are passed directly to pandas.to_numeric method.
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

#### clean_dataframe_column_names(dataframe, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789", special_treatment={})
Replace dataframe columns to only contain chars allowed in BigQuery tables column name.

special_treatment dictionary substitutes the terms in the keys by its value pair.

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

#### upload(self, dataframe, dataset, table, \*\*kwargs)
Prepare dataframe columns and executes an insert SQL command into BigQuery.

\*\*kwargs are passed directly to pandas.to_gbq method.
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

#### upload_from_gcs(self, dataset, table, gs_path, file_format="CSV", header_rows=1, delimiter=",", encoding="UTF-8", writing_mode="APPEND", create_table_if_needed=False, schema=None)
Uploads data from Google Cloud Storage directly to BigQuery.

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

#### upload_from_file(self, dataset, table, file_location, file_format="CSV", header_rows=1, delimiter=",", encoding="UTF-8", writing_mode="APPEND", create_table_if_needed=False, schema=None)
Uploads data from a local file to BigQuery.

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

#### start_transfer(self, project_path=None, project_name=None, transfer_name=None)
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

## gcloudstorage_tools
### GCloudStorageTool
This class handle most of the interaction needed with Google Cloud Storage,
so the base code becomes more readable and straightforward.

#### \_\_init\_\_(self, bucket=None, subfolder="", gs_path=None)
Takes a either gs_path or both bucket name and subfolder name as parameters to set the current working directory. It also opens a connection with Google Cloud Storage.

The paradigm of this class is that all the operations are done in the current working directory, so it is important to set the right path (you can reset it later, but still).

Usage example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")

# or

gs = GCloudStorageTool(bucket="some_other_bucket", subfolder="some_subfolder/subpath/")
```

#### bucket(self) @property
Returns the bucket object from the client based on the bucket name given in \_\_init\_\_ or set_bucket

#### set_bucket(self, bucket)
Takes a string as a parameter to reset the bucket name and bucket object. It has no return value.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")

gs.set_bucket("some_other_bucket")

# Check new path structure
print(gs.get_gs_path())
```

#### set_subfolder(self, subfolder)
Takes a string as a parameter to reset the subfolder name. It has no return value.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")

gs.set_subfolder("some/more_complex/subfolder/structure/")

# Check new path structure
print(gs.get_gs_path())
```

#### set_by_path(self, s3_path)
Takes a string as a parameter to reset the bucket name and subfolder name by its GS path. It has no return value.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")

gs.set_by_path("gs://some_other_bucket/some/more_complex/subfolder/structure/")

# Check new path structure
print(gs.get_gs_path())
```

#### get_gs_path(self)
Returns a string containing the GS path for the currently set bucket and subfolder. It takes no parameter.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")

print(gs.get_gs_path())
```

#### list_all_buckets(self)
Returns a list of all Buckets in Google Cloud Storage. It takes no parameter.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


# Setting or not a subfolder doesn't change the output of this function
gs = GCloudStorageTool(bucket="some_bucket")

all_buckets = gs.list_all_buckets()

# some code here
```

#### get_bucket_info(self, bucket=None)
Returns a dictionary with the information of Name, Datetime Created, Datetime Updated and Owner ID
of the currently selected bucket (or the one passed in the parameters).

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(bucket="some_bucket")

bucket_info = gs.get_bucket_info()
print(bucket_info)
```

#### list_bucket_attributes(self)
A list of all curently supported bucket attributes that comes in get_bucket_info method return dictionary.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(bucket="some_bucket")

bucket_info_attributes = gs.list_bucket_attributes()
print(bucket_info_attributes)
```

#### get_blob_info(self)
Converts a google.cloud.storage.Blob (which represents a storage object) to context format (GCS.BucketObject).

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(bucket="some_bucket", subfolder="some_subfolder")
gs.set_blob("some_subfolder/file.csv")

blob_info_attributes = gs.get_blob_info()
print(blob_info_attributes)
```

#### list_blob_attributes(self)
A list of all curently supported bucket attributes that comes in get_blob_info method return dictionary.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(bucket="some_bucket")
gs.set_blob("some_subfolder/file.csv")

blob_info_attributes = gs.list_blob_attributes()
print(blob_info_attributes)
```

#### list_contents(self, yield_results=False):
Lists all files that correspond with bucket and subfolder set at the initialization.

It can either return a list or yield a generator. Lists can be more familiar to use, but when dealing with large amounts of data, yielding the results may be a better option in terms of efficiency.

For more information on how to use generators and yield, check this video:
https://www.youtube.com/watch?v=bD05uGo_sVI

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")

path_contents = gs.list_contents()

if len(path_contents) == 0:
    s3.set_subfolder("logs/subfolder/")

    # When a specific bucket/ bucket + subfolder contains a lot of data,
    # that's when yielding the results may be more efficient.
    for file in gs.list_contents(yield_results=True):
        # Do something

# some code here
```

#### rename_file(self, new_filename, old_filename)
Not implemented.

#### rename_subfolder(self, new_subfolder)
Not implemented.

#### upload_file(self, filename, remote_path=None)
Uploads file to remote path in Google Cloud Storage (GS).

remote_path can take either a full GS path or a subfolder only one.

If the remote_path parameter is not set, it will default to whatever subfolder
is set in instance of the class plus the file name that is being uploaded.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


file_location = "C:\\Users\\USER\\Desktop\\file.csv"

gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")

# upload_file method accepts all 3 options
gs.upload_file(file_location)
gs.upload_file(file_location, "gs://some_bucket/other_subfolder/")
gs.upload_file(file_location, "another_subfolder/")  # Just subfolder
```

#### upload_subfolder(self, folder_path)
Not implemented.

#### download_file(self, fullfilename=None, replace=False)
Downloads remote gs file to local path.

If the fullfilename parameter is not set, it will default to the currently set blob.

If replace is set to True and there is already a file downloaded with the same filename and path,
it will replace the file. Otherwise it will create a new file with a number attached to the end.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


file_location = "gs://some_bucket/other_subfolder/"

gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")

# download_file method accepts both options
gs.download_file(file_location)
gs.download_file(file_location, "C:\\Users\\USER\\Desktop\\file.csv")
```

#### download_subfolder(self)
Not implemented.

#### download_on_dataframe(self, \*\*kwargs)
Use blob information to download file and use it directly on a Pandas DataFrame
without having to save the file.

\*\*kwargs are passed directly to pandas.read_csv method.
The complete documentation of this method can be found here:
https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


file_location = "gs://some_bucket/other_subfolder/"

gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")

# For a well behaved file, you may just use the method directly
gs.set_blob("subfolder/file.csv")
df = gs.download_on_dataframe()

# For a file with a weird layout, you may want to use some parameters to save some time in data treatment
gs.set_blob("subfolder/weird_file.csv")
df = gs.download_on_dataframe(sep=";", encoding="ISO-8859-1", decimal=",")
```

#### delete_file(self)
Not implemented.

#### delete_subfolder(self)
Not implemented.

## general_tools
### fetch_credentials(service_name, \*\*kwargs)
Gets the credentials from the secret file set in `CREDENTIALS_HOME` variable and returns the credentials of the selected service in a dictionary. If service is "credentials_path", a path is returned instead.

It's meant to be used basically by the other modules, not actually by the user of the library.

Usage example:
```
from instackup.general_tools import fetch_credentials

print(fetch_credentials(service_name="Google"))
print(fetch_credentials("AWS"))
print(fetch_credentials("RedShift", connection_type="cluster_credentials"))
print(fetch_credentials(service_name="PostgreSQL", connection="default"))
print(fetch_credentials("credentials_path"))
```

### unicode_to_ascii(unicode_string)
Replaces all non-ascii chars in string by the closest possible match.

This solution was inpired by this answer:
https://stackoverflow.com/a/517974/11981524

Usage example:
```
from instackup.general_tools import unicode_to_ascii


raw_data = "ÑÇÀÁÂÃÈÉÊÍÒÓÔÙÚ ñçàáâãèéêíòóôùú"
ascii_data = unicode_to_ascii(raw_data)

print(ascii_data)  # output: >>> ncaaaaeeeiooouu ncaaaaeeeiooouu
```

### parse_remote_uri(uri, service)
Parses a Google Cloud Storage (GS) or an Amazon S3 path into bucket and subfolder(s).
Raises an error if path is with wrong format.

service parameter can be either "gs" or "s3"

Usage example:
```
from instackup.general_tools import parse_remote_uri


### S3
s3_path = "s3://some_bucket/subfolder/"
bucket_name, subfolder = parse_remote_uri(s3_path, "s3")

print(f"Bucket name: {bucket_name}")  # output: >>> some_bucket
print(f"Subfolder: {subfolder}")      # output: >>> subfolder


### Storage
gs_path = "gs://some_bucket/subfolder/"
bucket_name, subfolder = parse_remote_uri(gs_path, "gs")

print(f"Bucket name: {bucket_name}")  # output: >>> some_bucket
print(f"Subfolder: {subfolder}")      # output: >>> subfolder
```

## heroku_tools
### HerokuTool
This class encapsulates and handle most of the interaction needed with Heroku CLI, so the base code becomes more readable and straightforward.

#### \_\_init\_\_(self, heroku_path="heroku", app=None, remote=None)
Initialization takes an optional parameter _heroku_path_ that's either the PATH variable or the actual path to the CLI app location in the system.

It also takes 2 extra optional parameters: _app_ and _remote_ that specify the current app in use. Doesn't need to fill both, just one is ok. If there's only one registered app, these parameter don't need to be filled.

Usage example:
```
from instackup.heroku_tools import HerokuTool

# Doesn't need to fill both app and remote parameters. This is just for an example.
heroku = HerokuTool(heroku_path="path/to/heroku", app="lavedonio", remote="heroku-staging")
```

#### app_flag(self) @property
Returns the app flag string that will be used as part of the program in execute method, based on the app or the remote parameters given in \_\_init\_\_.

#### execute(self, cmd)
Executes a Heroku command via the CLI and returns the output.

Usage example:
```
from instackup.heroku_tools import HerokuTool

heroku = HerokuTool(remote="heroku-staging")
result = heroku.execute("releases")

print(result)
```

## postgresql_tools
### PostgreSQLTool
This class handle most of the interaction needed with PostgreSQL, so the base code becomes more readable and straightforward.

This class implements the with statement, so there are 2 ways of using it.

**1st way:**

```
from instackup.postgresql_tools import PostgreSQLTool

with PostgreSQLTool() as pg:
    # use pg object to interact with PostgreSQL database
```

**2nd way:**

```
from instackup.postgresql_tools import PostgreSQLTool

pg = PostgreSQLTool()
pg.connect()

try:
    # use pg object to interact with PostgreSQL database
except Exception as e:
    pg.rollback()
    raise e
else:
    pg.commit()
finally:
    pg.close_connection()
```

Easy to see that it is recommended (and easier) to use the first syntax.

#### \_\_init\_\_(self, connect_by_cluster=True)
Initialization takes connect_by_cluster parameter that sets connection type and has no return value.

The \_\_init\_\_ method doesn't actually opens the connection, but sets all values required by the connect method.

Usage example:
```
from instackup.postgresql_tools import PostgreSQLTool

pg = PostgreSQLTool()
```

#### connect(self, fail_silently=False)
Create the connection using the \_\_init\_\_ attributes and returns its own object for with statement.

If fail_silently parameter is set to True, any errors will be surpressed and not stop the code execution.

Usage example:
```
from instackup.postgresql_tools import PostgreSQLTool

pg = PostgreSQLTool()
pg.connect()
# remember to close the connection later

# or

with PostgreSQLTool() as pg:
    # Already connected, use pg object in this context

```

#### commit(self)
Commits any pending transaction to the database. It has no extra parameter or return value.

Usage example:
```
from instackup.postgresql_tools import PostgreSQLTool

pg = PostgreSQLTool()
pg.connect()
# Do stuff
pg.commit()
# remember to close the connection later

# or

with PostgreSQLTool() as pg:
    # Already connected, use pg object in this context

    # Do stuff

    # No need to explictly commit as it will do when leaving this context, but nonetheless:
    pg.commit()
```

#### rollback(self)
Roll back to the start of any pending transaction. It has no extra parameter or return value.

Usage example:
```
from instackup.postgresql_tools import PostgreSQLTool

pg = PostgreSQLTool()
pg.connect()

try:
    # Do stuff
except Exception as e:
    pg.rollback()
    raise e
else:
    pg.commit()
finally:
    # remember to close the connection later
    pg.close_connection()

# or

with PostgreSQLTool() as pg:
    # Already connected, use pg object in this context

    # Do stuff
    
    # No need to explictly commit or rollback as it will do when leaving this context, but nonetheless:
    if meet_condition:
        pg.commit()
    else:
        pg.rollback()
```

#### execute_sql(self, command, fail_silently=False)
Execute a SQL command (CREATE, UPDATE and DROP). It has no return value.

If fail_silently parameter is set to True, any errors will be surpressed and not stop the code execution.

Usage example:
```
from instackup.postgresql_tools import PostgreSQLTool


sql_cmd = """CREATE TABLE test (
    id          integer NOT NULL CONSTRAINT firstkey PRIMARY KEY,
    username    varchar(40) UNIQUE NOT NULL,
    fullname    varchar(64) NOT NULL,
    created_at  TIMESTAMP NOT NULL,
    last_login  TIMESTAMP
);
"""


pg = PostgreSQLTool()
pg.connect()

try:
    # Execute the command
    pg.execute_sql(sql_cmd)

except Exception as e:
    pg.rollback()
    raise e
else:
    pg.commit()
finally:
    # remember to close the connection later
    pg.close_connection()

# or

with PostgreSQLTool() as pg:
    # Already connected, use pg object in this context

    # This command would throw an error (since the table already was created before),
    # but since fail_silently parameter is set to True, it'll catch the exception
    # and let the code continue past this point.
    pg.execute_sql(sql_cmd, fail_silently=True)

    # other code
```

#### query(self, sql_query, fetch_through_pandas=True, fail_silently=False)
Run a query and return the results.

fetch_through_pandas parameter tells if the query should be parsed by psycopg2 cursor or pandas.

If fail_silently parameter is set to True, any errors will be surpressed and not stop the code execution.

Usage example:
```
from instackup.postgresql_tools import PostgreSQLTool


sql_query = """SELECT * FROM table LIMIT 100"""


pg = PostgreSQLTool()
pg.connect()

try:
    # Returns a list of tuples containing the rows of the response
    table = pg.query(sql_cmd, fetch_through_pandas=False, fail_silently=True)

    # Do something with table variable

except Exception as e:
    pg.rollback()
    raise e
else:
    pg.commit()
finally:
    # remember to close the connection later
    pg.close_connection()

# or

with PostgreSQLTool() as pg:
    # Already connected, use pg object in this context

    # Returns a Pandas dataframe
    df = pg.query(sql_cmd)

    # To do operations with dataframe, you'll need to import pandas library

    # other code
```

#### close_connection(self)
Closes Connection with PostgreSQL database. It has no extra parameter or return value.

Usage example:
```
from instackup.postgresql_tools import PostgreSQLTool

pg = PostgreSQLTool()
pg.connect()

try:
    # Do stuff
except Exception as e:
    pg.rollback()
    raise e
else:
    pg.commit()
finally:
    pg.close_connection()

# or

with PostgreSQLTool() as pg:
    # Already connected, use pg object in this context

    # Do stuff

    # Will close the connection automatically when existing this scope
```

## redshift_tools
### RedShiftTool
This class handle most of the interaction needed with RedShift, so the base code becomes more readable and straightforward.

This class implements the with statement, so there are 2 ways of using it.

**1st way:**

```
from instackup.redshift_tools import RedShiftTool

with RedShiftTool() as rs:
    # use rs object to interact with RedShift database
```

**2nd way:**

```
from instackup.redshift_tools import RedShiftTool

rs = RedShiftTool()
rs.connect()

try:
    # use rs object to interact with RedShift database
except Exception as e:
    rs.rollback()
    raise e
else:
    rs.commit()
finally:
    rs.close_connection()
```

Easy to see that it is recommended (and easier) to use the first syntax.

#### \_\_init\_\_(self, connect_by_cluster=True)
Initialization takes connect_by_cluster parameter that sets connection type and has no return value.

The \_\_init\_\_ method doesn't actually opens the connection, but sets all values required by the connect method.

Usage example:
```
from instackup.redshift_tools import RedShiftTool

rs = RedShiftTool()
```

#### connect(self, fail_silently=False)
Create the connection using the \_\_init\_\_ attributes and returns its own object for with statement.

If fail_silently parameter is set to True, any errors will be surpressed and not stop the code execution.

Usage example:
```
from instackup.redshift_tools import RedShiftTool

rs = RedShiftTool()
rs.connect()
# remember to close the connection later

# or

with RedShiftTool() as rs:
    # Already connected, use rs object in this context

```

#### commit(self)
Commits any pending transaction to the database. It has no extra parameter or return value.

Usage example:
```
from instackup.redshift_tools import RedShiftTool

rs = RedShiftTool()
rs.connect()
# Do stuff
rs.commit()
# remember to close the connection later

# or

with RedShiftTool() as rs:
    # Already connected, use rs object in this context

    # Do stuff

    # No need to explictly commit as it will do when leaving this context, but nonetheless:
    rs.commit()
```

#### rollback(self)
Roll back to the start of any pending transaction. It has no extra parameter or return value.

Usage example:
```
from instackup.redshift_tools import RedShiftTool

rs = RedShiftTool()
rs.connect()

try:
    # Do stuff
except Exception as e:
    rs.rollback()
    raise e
else:
    rs.commit()
finally:
    # remember to close the connection later
    rs.close_connection()

# or

with RedShiftTool() as rs:
    # Already connected, use rs object in this context

    # Do stuff
    
    # No need to explictly commit or rollback as it will do when leaving this context, but nonetheless:
    if meet_condition:
        rs.commit()
    else:
        rs.rollback()
```

#### execute_sql(self, command, fail_silently=False)
Execute a SQL command (CREATE, UPDATE and DROP). It has no return value.

If fail_silently parameter is set to True, any errors will be surpressed and not stop the code execution.

Usage example:
```
from instackup.redshift_tools import RedShiftTool


sql_cmd = """CREATE TABLE test (
    id          integer NOT NULL CONSTRAINT firstkey PRIMARY KEY,
    username    varchar(40) UNIQUE NOT NULL,
    fullname    varchar(64) NOT NULL,
    created_at  TIMESTAMP NOT NULL,
    last_login  TIMESTAMP
);
"""


rs = RedShiftTool()
rs.connect()

try:
    # Execute the command
    rs.execute_sql(sql_cmd)

except Exception as e:
    rs.rollback()
    raise e
else:
    rs.commit()
finally:
    # remember to close the connection later
    rs.close_connection()

# or

with RedShiftTool() as rs:
    # Already connected, use rs object in this context

    # This command would throw an error (since the table already was created before),
    # but since fail_silently parameter is set to True, it'll catch the exception
    # and let the code continue past this point.
    rs.execute_sql(sql_cmd, fail_silently=True)

    # other code
```

#### query(self, sql_query, fetch_through_pandas=True, fail_silently=False)
Run a query and return the results.

fetch_through_pandas parameter tells if the query should be parsed by psycopg2 cursor or pandas.

If fail_silently parameter is set to True, any errors will be surpressed and not stop the code execution.

Usage example:
```
from instackup.redshift_tools import RedShiftTool


sql_query = """SELECT * FROM table LIMIT 100"""


rs = RedShiftTool()
rs.connect()

try:
    # Returns a list of tuples containing the rows of the response
    table = rs.query(sql_cmd, fetch_through_pandas=False, fail_silently=True)

    # Do something with table variable

except Exception as e:
    rs.rollback()
    raise e
else:
    rs.commit()
finally:
    # remember to close the connection later
    rs.close_connection()

# or

with RedShiftTool() as rs:
    # Already connected, use rs object in this context

    # Returns a Pandas dataframe
    df = rs.query(sql_cmd)

    # To do operations with dataframe, you'll need to import pandas library

    # other code
```

#### unload_to_S3(self, redshift_query, s3_path, filename, unload_options="MANIFEST GZIP ALLOWOVERWRITE REGION 'us-east-2'")
Executes an unload command in RedShift database to copy data to S3.

Takes the parameters redshift_query to grab the data, s3_path to set the location of copied data, filename as the custom prefix of the file and unload options.

Unload options can be better understood in this link: https://docs.aws.amazon.com/redshift/latest/dg/r_UNLOAD.html

Usage example:
```
from instackup.redshift_tools import RedShiftTool


# Maybe you'll get this timestamp from other source
timestamp = '2019-11-29 19:31:42.766000+00:00'
extraction_query = """SELECT * FROM schema.table WHERE tstamp = '{timestamp}'""".format(timestamp=timestamp)

s3_path = "s3://redshift-data/unload/"
filename = "file_"
unload_options = "DELIMITER '|' ESCAPE ADDQUOTES"


rs = RedShiftTool()
rs.connect()

try:
    # Unload data with custom options
    rs.unload_to_S3(extraction_query, s3_path, filename, unload_options)

except Exception as e:
    rs.rollback()
    raise e
else:
    rs.commit()
finally:
    # remember to close the connection later
    rs.close_connection()

# or

with RedShiftTool() as rs:
    # Already connected, use rs object in this context

    # Unload data without custom options (will overwrite)
    rs.unload_to_S3(extraction_query, s3_path, filename)

    # other code
```

#### close_connection(self)
Closes Connection with RedShift database. It has no extra parameter or return value.

Usage example:
```
from instackup.redshift_tools import RedShiftTool

rs = RedShiftTool()
rs.connect()

try:
    # Do stuff
except Exception as e:
    rs.rollback()
    raise e
else:
    rs.commit()
finally:
    rs.close_connection()

# or

with RedShiftTool() as rs:
    # Already connected, use rs object in this context

    # Do stuff

    # Will close the connection automatically when existing this scope
```

## s3_tools
### S3Tool
This class handle most of the interaction needed with S3,
so the base code becomes more readable and straightforward.

To understand the S3 structure, you need to know it is not a hierarchical filesystem,
it is only a key-value store, though the key is often used like a file path for organising data,
prefix + filename. More information about this can be read in this StackOverFlow thread:
https://stackoverflow.com/questions/52443839/s3-what-exactly-is-a-prefix-and-what-ratelimits-apply

All that means is that while you may see a path as:
```
s3://bucket-1/folder1/subfolder1/some_file.csv
root| folder | sub.1 |  sub.2   |    file    |
```

It is actually:
```
s3://bucket-1/folder1/sub1/file.csv
root| bucket |         key        |
```

A great (not directly related) thread that can help that sink in (and help understand some methods here)
is this one: https://stackoverflow.com/questions/35803027/retrieving-subfolders-names-in-s3-bucket-from-boto3

In this class, all keys and keys prefix are being treated as a folder tree structure,
since the reason for this to exists is to make the programmers interactions with S3
easier to write and the code easier to read.

#### \_\_init\_\_(self, bucket=None, subfolder="", s3_path=None)
Takes either a s3_path or both bucket name and subfolder name as parameters to set the current working directory. It also opens a connection with AWS S3.

The paradigm of this class is that all the operations are done in the current working directory, so it is important to set the right path (you can reset it later, but still).

Usage example:
```
from instackup.s3_tools import S3Tool


s3 = S3Tool(s3_path="s3://some_bucket/subfolder/")

# or

s3 = S3Tool(bucket="some_other_bucket", subfolder="some_subfolder/subpath/")
```

#### bucket(self) @property
Returns the bucket object from the client based on the bucket name given in \_\_init\_\_ or set_bucket

#### set_bucket(self, bucket)
Takes a string as a parameter to reset the bucket name and bucket object. It has no return value.

Usage Example:
```
from instackup.s3_tools import S3Tool


s3 = S3Tool(s3_path="s3://some_bucket/subfolder/")

s3.set_bucket("some_other_bucket")

# Check new path structure
print(s3.get_s3_path())
```

#### set_subfolder(self, subfolder)
Takes a string as a parameter to reset the subfolder name. It has no return value.

Usage Example:
```
from instackup.s3_tools import S3Tool


s3 = S3Tool(s3_path="s3://some_bucket/subfolder/")

s3.set_subfolder("some/more_complex/subfolder/structure/")

# Check new path structure
print(s3.get_s3_path())
```

#### set_by_path(self, s3_path)
Takes a string as a parameter to reset the bucket name and subfolder name by its S3 path. It has no return value.

Usage Example:
```
from instackup.s3_tools import S3Tool


s3 = S3Tool(s3_path="s3://some_bucket/subfolder/")

s3.set_by_path("s3://some_other_bucket/some/more_complex/subfolder/structure/")

# Check new path structure
print(s3.get_s3_path())
```

#### get_s3_path(self)
Returns a string containing the S3 path for the currently set bucket and subfolder. It takes no parameter.

Usage Example:
```
from instackup.s3_tools import S3Tool


s3 = S3Tool(bucket="some_bucket", subfolder="subfolder/")

print(s3.get_s3_path())
```

#### rename_file(self, new_filename, old_filename)
Takes 2 strings containing file names and rename only the filename from path key, so the final result is similar to rename a file. It has no return value.

Usage Example:
```
from instackup.s3_tools import S3Tool


s3 = S3Tool(bucket="some_bucket", subfolder="subfolder/")

s3.rename_file("new_name", "old_name")
```

#### rename_subfolder(self, new_subfolder)
Takes a string containing the new subfolder name and renames all keys in the currently set path, so the final result is similar to rename a subfolder. It has no return value.

Usage Example:
```
from instackup.s3_tools import S3Tool


old_subfolder = "some/more_complex/subfolder/structure/"
new_subfolder = "some/new/subfolder/structure/"

s3 = S3Tool(bucket="some_bucket", subfolder=old_subfolder)

# The final result is similar to just rename the "more_complex" folder to "new"
s3.rename_subfolder(new_subfolder)
```

#### list_all_buckets(self)
Returns a list of all Buckets in S3. It takes no parameter.

Usage Example:
```
from instackup.s3_tools import S3Tool


# Setting or not a subfolder doesn't change the output of this function
s3 = S3Tool(bucket="some_bucket")

all_buckets = s3.list_all_buckets()

# some code here
```

#### list_contents(self, yield_results=False):
Lists all files that correspond with bucket and subfolder set at the initialization.

It can either return a list or yield a generator. Lists can be more familiar to use, but when dealing with large amounts of data, yielding the results may be a better option in terms of efficiency.

For more information on how to use generators and yield, check this video:
https://www.youtube.com/watch?v=bD05uGo_sVI

Usage Example:
```
from instackup.s3_tools import S3Tool


s3 = S3Tool(s3_path="s3://some_bucket/subfolder/")

path_contents = s3.list_contents()

if len(path_contents) == 0:
    s3.set_subfolder("logs/subfolder/")

    # When a specific bucket/ bucket + subfolder contains a lot of data,
    # that's when yielding the results may be more efficient.
    for file in s3.list_contents(yield_results=True):
        # Do something

# some code here
```

#### upload_file(self, filename, remote_path=None)
Uploads file to remote path in S3.

remote_path can take either a full S3 path or a subfolder only one. It has no return value.

If the remote_path parameter is not set, it will default to whatever subfolder
is set in instance of the class plus the file name that is being uploaded.

Usage Example:
```
from instackup.s3_tools import S3Tool


file_location = "C:\\Users\\USER\\Desktop\\file.csv"

s3 = S3Tool(s3_path="s3://some_bucket/subfolder/")

# upload_file method accepts all 3 options
s3.upload_file(file_location)
s3.upload_file(file_location, "s3://some_bucket/other_subfolder/")
s3.upload_file(file_location, "another_subfolder/")  # Just subfolder
```

#### upload_subfolder(self, folder_path)
Not implemented.

#### download_file(self, remote_path, filename=None)
Downloads remote S3 file to local path.

remote_path can take either a full S3 path or a subfolder only one. It has no return value.

If the filename parameter is not set, it will default to whatever subfolder
is set in instance of the class plus the file name that is being downloaded.

Usage Example:
```
from instackup.s3_tools import S3Tool


file_desired_location = "C:\\Users\\USER\\Desktop\\file.csv"
remote_location = "s3://some_bucket/other_subfolder/file.csv"

s3 = S3Tool(s3_path="s3://some_bucket/subfolder/")

# download_file method accepts both options
s3.download_file(remote_location)
s3.download_file(remote_location, file_desired_location)
```

#### download_subfolder(self)
Not implemented.

#### delete_file(self, filename, fail_silently=False)
Deletes file from currently set path. It has no return value.

Raises an error if file doesn't exist and fail_silently parameter is set to False.

Usage Example:
```
from instackup.s3_tools import S3Tool


filename = "file.csv"

s3 = S3Tool(s3_path="s3://some_bucket/subfolder/")

s3.delete_file(file_location)

# Will fail to delete the same file it was deleted before,
# but won't raise any error due to fail_silently being set to True
s3.delete_file(file_location, fail_silently=True)
```

#### delete_subfolder(self)
Deletes all files with subfolder prefix, so the final result is similar to deleting a subfolder. It has no return value.

Raises an error if file doesn't exist and fail_silently parameter is set to False.

Once the subfolder is deleted, it resets to no extra path (empty subfolder name).

Usage Example:
```
from instackup.s3_tools import S3Tool


filename = "file.csv"

s3 = S3Tool(s3_path="s3://some_bucket/subfolder/")

s3.delete_folder()

# Check new path structure
print(s3.get_s3_path())
```

# Version log
See what changed in every version.

### Version 0.0.5 (alpha)
Fifth alpha release.

#### Added modules:
- heroku_tools
- postgresql_tools

Inside those modules, these classes and functions/methods were added:
- HerokuTool
  - \_\_init\_\_
  - app_flag @property
  - execute
- PostgreSQLTool
  - \_\_init\_\_
  - connect
  - commit
  - rollback
  - execute_sql
  - query
  - unload_to_S3
  - close_connection
  - \_\_enter\_\_
  - \_\_exit\_\_

#### New functionalities:
- bigquery_tools
  - BigQueryTool
    - convert_postgresql_table_schema
    - convert_multiple_postgresql_tables_schema

#### Modified functionalities:
- general_tools
  - fetch_credentials

#### Bug fixes:
- BigQueryTool.convert_dataframe_to_numeric and BigQueryTool.clean_dataframe_column_names methods were failing because the self parameter was missing.

#### Functionalities still in development:
- gcloudstorage_tools
  - GCloudStorageTool
    - rename_file
    - rename_subfolder
    - upload_subfolder
    - download_subfolder
    - delete_file
    - delete_subfolder
- s3_tools
  - S3Tool
    - upload_subfolder
    - download_subfolder

### Version 0.0.4 (alpha)
Fourth alpha release.

#### New functionalities:
- bigquery_tools
  - BigQueryTool
    - query_and_save_results

#### Modified functionalities:
- general_tools
  - fetch_credentials

#### Functionalities still in development:
- gcloudstorage_tools
  - GCloudStorageTool
    - rename_file
    - rename_subfolder
    - upload_subfolder
    - download_subfolder
    - delete_file
    - delete_subfolder
- s3_tools
  - S3Tool
    - upload_subfolder
    - download_subfolder

### Version 0.0.3 (alpha)
Third alpha release.

#### New functionalities:
- bigquery_tools
  - BigQueryTool
    - list_datasets
    - list_tables_in_dataset
    - get_table_schema
    - \_\_job_preparation_file_upload (private method)
    - upload_from_gcs
    - upload_from_file

#### Functionalities still in development:
- gcloudstorage_tools
  - GCloudStorageTool
    - rename_file
    - rename_subfolder
    - upload_subfolder
    - download_subfolder
    - delete_file
    - delete_subfolder
- s3_tools
  - S3Tool
    - upload_subfolder
    - download_subfolder

### Version 0.0.2 (alpha)
Second alpha release.

#### Added modules:
- gcloudstorage_tools

Inside this module, these classes and functions/methods were added:
- GCloudStorageTool
  - \_\_init\_\_
  - bucket @property
  - set_bucket
  - set_subfolder
  - set_blob
  - set_by_path
  - get_gs_path
  - list_all_buckets
  - get_bucket_info
  - list_bucket_attributes
  - get_blob_info
  - list_blob_attributes
  - list_contents
  - upload_file
  - download_file
  - download_on_dataframe

#### New functionalities:
- bigquery_tools
  - BigQueryTool
    - convert_dataframe_to_numeric
    - clean_dataframe_column_names
- general_tools
  - unicode_to_ascii
  - parse_remote_uri

#### Modified functionalities:
- bigquery_tools
  - BigQueryTool
    - upload

#### Deleted functionalities:
- gcloudstorage_tools
  - parse_gs_path
- s3_tools
  - parse_s3_path

#### Functionalities still in development:
- gcloudstorage_tools
  - GCloudStorageTool
    - rename_file
    - rename_subfolder
    - upload_subfolder
    - download_subfolder
    - delete_file
    - delete_subfolder
- s3_tools
  - S3Tool
    - upload_subfolder
    - download_subfolder

### Version 0.0.1 (alpha)
First alpha release:

#### Added modules:
- bigquery_tools
- general_tools
- redshift_tools
- s3_tools

Inside those modules, these classes and functions/methods were added:
- BigQueryTool
  - \_\_init\_\_
  - query
  - upload
  - start_transfer
- fetch_credentials
- RedShiftTool
  - \_\_init\_\_
  - connect
  - commit
  - rollback
  - execute_sql
  - query
  - unload_to_S3
  - close_connection
  - \_\_enter\_\_
  - \_\_exit\_\_
- parse_s3_path
- S3Tool
  - \_\_init\_\_
  - bucket @property
  - set_bucket
  - set_subfolder
  - set_by_path
  - get_s3_path
  - rename_file
  - rename_subfolder
  - list_all_buckets
  - list_contents
  - upload_file
  - download_file
  - delete_file
  - delete_subfolder

#### Modules still in development:
- gcloudstorage_tools

Inside this module, these classes and functions/methods are in development:
- parse_gs_path
- GCloudStorageTool
  - \_\_init\_\_
  - bucket @property
  - set_bucket
  - set_subfolder
  - set_by_path
  - get_gs_path
  - list_all_buckets
  - list_bucket_contents
  - upload_file
  - download_file
- S3Tool
  - upload_subfolder
  - download_subfolder
