# Instackup
This Python library is an open source way to standardize and simplify connections with cloud-based tools and databases and commonly used tools in data manipulation and analysis.

# Index

- [Prerequisites](https://github.com/Lavedonio/instackup#prerequisites)
- [Installation](https://github.com/Lavedonio/instackup#installation)
- [Documentation](https://github.com/Lavedonio/instackup#documentation)
	- [bigquery_tools](https://github.com/Lavedonio/instackup#bigquery_tools)
	- [gcloudstorage_tools](https://github.com/Lavedonio/instackup#gcloudstorage_tools)
	- [redshift_tools](https://github.com/Lavedonio/instackup#redshift_tools)
	- [s3_tools](https://github.com/Lavedonio/instackup#s3_tools)

# Prerequisites
1. Have a [Python 3.6 version or superior](https://www.python.org/downloads/) installed;
2. Create a YAML file with credentials information;
3. [Optional but recommended] Configure an Environment Variable that points where the Credentials file is.

### 1. Have a Python 3.6 version or superior installed
Got to this [link](https://www.python.org/downloads/) e download the most current version that is compatible with this package.

### 2. Create a YAML file with credentials information

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
  secret_key: ÇçasldUYkfsadçSDadskfDSDAsdUYalf

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
```
Save this file with `.yml` extension in a folder where you know the path won't be modified, like the Desktop folder (Example: `C:\Users\USER\Desktop\Credentials\secret.yml`).

### 3. [Optional but recommended] Configure an Environment Variable that points where the Credentials file is.

To configure the Environment Variable, follow the instructions bellow, based on your Operating System.

#### Windows
1. Place the YAML file in a folder you won't change its name or path later;
2. In Windows Search, type `Environment Variables` and click in the Control Panel result;
3. Click on the button `Environment Variables...`;
4. In **Environment Variables**, click on the button `New`;
5. In **Variable name** type `CREDENTIALS_HOME` and in **Variable value** paste the full path to the recently created YAML file;
6. Click **Ok** in the 3 open windows.

#### Linux/MacOS
1. Place the YAML file in a folder you won't change its name or path later;
2. Open the file `.bashrc`. If it doesn't exists, create one in the `HOME` directory. If you don't know how to get there, open the Terminal, type `cd` and then **ENTER**;
3. Inside the file, in a new line, type the command: `export CREDENTIALS_HOME="/path/to/file"`, replacing the content inside quotes by the full path to the recently created YAML file;
4. Save the file and restart all open Terminal windows.

> **Note:** If you don't follow this last prerequisite, you need to set the environment variable manually inside the code. To do that, inside your python code, after the imports, type the command (replacing the content inside quotes by the full path to the recently created YAML file):

```
os.environ["CREDENTIALS_HOME"] = "/path/to/file"
```

# Installation
Go to the Terminal and type:

    pip install -i https://test.pypi.org/simple/ instackup

# Documentation
## bigquery_tools
### BigQuery_Tool
This class handle most of the interaction needed with BigQuery, so the base code becomes more readable and straightforward.

#### __init__(self)
Initialization takes no parameter and has no return value. It sets the bigquery client.

Usage example:
```
from instackup.bigquery import BigQueryTool

bq = BigQueryTool()
```

#### query(self, sql_query)
Run a SQL query and return the results as a Pandas Dataframe.

Usage example:
```
import pandas as pd
from instackup.bigquery import BigQueryTool

bq = BigQueryTool()

sql_query = """SELECT * FROM `project_name.dataset.table`"""
df = bq.query(sql_query)
```

#### upload(self, dataframe, dataset, table, if_exists='fail')
Executes an insert SQL command into BigQuery

if_exists can take 3 different arguments:
- 'fail': If table exists, raises error.
- 'replace': If table exists, drop it, recreate it, and insert data.
- 'append': If table exists, insert data. Create if does not exist.

Full documentation for Pandas export to BigQuery can be found here:
https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_gbq.html

Usage example:
```
import pandas as pd
from instackup.bigquery import BigQueryTool

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

#### start_transfer(self, project_path=None, project_name=None, transfer_name=None)
Takes a project path or both project name and transfer name to trigger a transfer to start executing in BigQuery Transfer. Returns a status indicating if the request was processed (if it does, the response should be 'PENDING').
API documentation: https://googleapis.dev/python/bigquerydatatransfer/latest/gapic/v1/api.html

Usage example:
```
from instackup.bigquery import BigQueryTool

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
*To be defined...*

## general_tools
### fetch_credentials(service_name, \*\*kwargs)
Gets the credentials from the secret file set in CREDENTIALS_HOME variable and returns the credentials of the selected service in a dictionary. If service is "credentials_path", a path is returned instead.

It's meant to be used basically by the other modules, not actually by the user of the library.

Usage example:
```
from instackup.general_tools import fetch_credentials

print(fetch_credentials(service_name="Google"))
print(fetch_credentials("AWS"))
print(fetch_credentials("RedShift", connection_type="cluster_credentials"))
print(fetch_credentials("credentials_path"))
```

## redshift_tools
### RedShiftTool
This class handle most of the interaction needed with RedShift, so the base code becomes more readable and straightforward.

This class implements the with statement, so there are 2 ways of using it.

1st way:

```
from instackup.redshift_tools import RedShiftTool

with RedShiftTool() as rs:
    # use rs object to interact with RedShift database
```

2nd way:

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

#### __init__(self, connect_by_cluster=True)
Initialization takes connect_by_cluster parameter that sets connection type and has no return value.

The __init__ method doesn't actually opens the connection, but sets all values required by the connect method.

Usage example:
```
from instackup.bigquery import RedShiftTool

rs = RedShiftTool()
```

#### connect(self, fail_silently=False)
Create the connection using the __init__ attributes and returns its own object for with statement.

If fail_silently parameter is set to True, any errors will be surpressed and not stop the code execution.

Usage example:
```
from instackup.bigquery import RedShiftTool

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
from instackup.bigquery import RedShiftTool

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
from instackup.bigquery import RedShiftTool

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
from instackup.bigquery import RedShiftTool


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
from instackup.bigquery import RedShiftTool


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
from instackup.bigquery import RedShiftTool


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
from instackup.bigquery import RedShiftTool

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
### parse_s3_path(s3_path)
Parses a S3 path (s3_path parameter) into bucket and subfolder(s) and returns its values.

Raises an error if S3 path is with wrong format.

Usage example:
```
from instackup.s3_tools import parse_s3_path


s3_path = "s3://some_bucket/subfolder/"

bucket_name, subfolder = parse_s3_path()

print(f"Bucket name: {bucket_name}")
print(f"Subfolder: {subfolder}")
```

### S3Tool
This class handle most of the interaction needed with S3,
so the base code becomes more readable and straightforward.

To understand the S3 structure, you need to know it is not a hierarchical filesystem,
it is only a key-value store, though the key is often used like a file path for organising data,
prefix + filename. More information about this can be read in this StackOverFlow thread:
https://stackoverflow.com/questions/52443839/s3-what-exactly-is-a-prefix-and-what-ratelimits-apply

All that means is that while you may see a path as:

s3://bucket-1/folder1/subfolder1/some_file.csv

root| folder | sub.1 |  sub.2   |    file    |

It is actually:

s3://bucket-1/folder1/sub1/file.csv

root| bucket |         key        |

A great (not directly related) thread that can help that sink in (and help understand some methods here)
is this one: https://stackoverflow.com/questions/35803027/retrieving-subfolders-names-in-s3-bucket-from-boto3

In this class, all keys and keys prefix are being treated as a folder tree structure,
since the reason for this to exists is to make the programmers interactions with S3
easier to write and the code easier to read.

#### __init__(self, bucket=None, subfolder="", s3_path=None)
Takes a either s3_path or both bucket name and subfolder name as parameters to set the current working directory. It also opens a connection with AWS S3.

The paradigm of this class is that all the operations are done in the current working directory, so it is important to set the right path (you can reset it later, but still).

Usage example:
```
from instackup.s3_tools import S3Tool


s3 = S3Tool(s3_path="s3://some_bucket/subfolder/")

# or

s3 = S3Tool(bucket="some_other_bucket", subfolder="some_subfolder/subpath/")
```

#### bucket(self) @property
Returns the bucket object from the client based on the bucket name given in __init__ or set_bucket

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


s3 = S3Tool(bucket="some_bucket")

# Setting or not a subfolder doesn't change the output of this function
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


file_location = "C:\\Users\\USER\\Desktop\\file.csv"

s3 = S3Tool(s3_path="s3://some_bucket/subfolder/")

# upload_file method accepts all 3 options
s3.upload_file(file_location)
s3.upload_file(file_location, "s3://some_bucket/other_subfolder/")
s3.upload_file(file_location, "another_subfolder/")  # Just subfolder
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
