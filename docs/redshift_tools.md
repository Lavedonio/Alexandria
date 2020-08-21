# redshift_tools
This is the documentation for the redshift_tools module and all its contents, with usage examples.

# Index
- [RedShiftTool](#redshifttool)
  - [\_\_init\_\_(self, connect_by_cluster=True)](#__init__self-connect_by_clustertrue)
  - [connect(self, fail_silently=False)](#connectself-fail_silentlyfalse)
  - [commit(self)](#commitself)
  - [rollback(self)](#rollbackself)
  - [close_connection(self)](#close_connectionself)
  - [execute_sql(self, command, fail_silently=False)](#execute_sqlself-command-fail_silentlyfalse)
  - [query(self, sql_query, fetch_through_pandas=True, fail_silently=False)](#queryself-sql_query-fetch_through_pandastrue-fail_silentlyfalse)
  - [describe_table(self, table, schema="public", fetch_through_pandas=True, fail_silently=False)](#describe_tableself-table-schemapublic-fetch_through_pandastrue-fail_silentlyfalse)
  - [get_all_db_info(self, get_json_info=True, fetch_through_pandas=True, fail_silently=False)](#get_all_db_infoself-get_json_infotrue-fetch_through_pandastrue-fail_silentlyfalse)
  - [unload_to_S3(self, redshift_query, s3_path, filename, unload_options="MANIFEST GZIP ALLOWOVERWRITE REGION 'us-east-2'")](#unload_to_s3self-redshift_query-s3_path-filename-unload_optionsmanifest-gzip-allowoverwrite-region-us-east-2)

# Module Contents
## RedShiftTool
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

### \_\_init\_\_(self, connect_by_cluster=True)
Initialization takes _connect_by_cluster_ parameter, which sets connection type. It has no return value.

The \_\_init\_\_ method doesn't actually opens the connection, but sets all values required by the connect method.

Usage example:
```
from instackup.redshift_tools import RedShiftTool

rs = RedShiftTool()
```

### connect(self, fail_silently=False)
Create the connection using the \_\_init\_\_ attributes and returns its own object for with statement.

If _fail_silently_ parameter is set to True, any errors will be surpressed and not stop the code execution.

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

### commit(self)
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

### rollback(self)
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

### close_connection(self)
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

### execute_sql(self, command, fail_silently=False)
Execute a SQL _command_ (CREATE, UPDATE and DROP). It has no return value.

If _fail_silently_ parameter is set to True, any errors will be surpressed and not stop the code execution.

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

### query(self, sql_query, fetch_through_pandas=True, fail_silently=False)
Run a query and return the results.

_fetch_through_pandas_ parameter tells if the query should be parsed by psycopg2 cursor or pandas.

If _fail_silently_ parameter is set to True, any errors will be surpressed and not stop the code execution.

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

### describe_table(self, table, schema="public", fetch_through_pandas=True, fail_silently=False)
Special query that returns all metadata from a specific table.

Usage example:
```
from instackup.redshift_tools import RedShiftTool


rs = RedShiftTool()
rs.connect()

try:
    # Returns a list of tuples containing the rows of the response (Table: public.users)
    table = rs.describe_table("users", fetch_through_pandas=False, fail_silently=True)

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

    # Returns a Pandas dataframe with all schema info of that specific schema.table
    # To do operations with dataframe, you'll need to import pandas library
    df = rs.describe_table("airflow_logs", schema="another_schema")

    # other code
```

### get_all_db_info(self, get_json_info=True, fetch_through_pandas=True, fail_silently=False)
Gets all Database info, using a INFORMATION_SCHEMA query.

Ignore table pg_stat_statements and tables inside schemas pg_catalog and information_schema.

If _get_json_info_ parameter is True, it adds 2 columns with the data types from each key inside json and jsonb columns.

_fetch_through_pandas_ and _fail_silently_ parameters are passed directly to the _query_ method if _get_json_info_ parameter is set to False; if it's not, these 2 parameters are passed as their default values.

Returns a DataFrame if either _get_json_info_ or _fetch_through_pandas_ parameters are set to True; otherwise returns a list of tuples, each representing a row, with their position in the same order as in the columns of the INFORMATION_SCHEMA.COLUMNS table.

Usage example:
```
from instackup.redshift_tools import RedShiftTool


rs = RedShiftTool()
rs.connect()

try:
    # Returns a list of tuples containing the rows of the response
    schema_info = rs.get_all_db_info(get_json_info=False, fetch_through_pandas=False, fail_silently=True)

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

    # Returns a Pandas dataframe with all schema info, including inside JSON and JSONB fields
    # To do operations with dataframe, you'll need to import pandas library
    df = rs.get_all_db_info()

    # other code
```

### unload_to_S3(self, redshift_query, s3_path, filename, unload_options="MANIFEST GZIP ALLOWOVERWRITE REGION 'us-east-2'")
Executes an unload command in RedShift database to copy data to S3.

Takes the parameters _redshift_query_ to grab the data, _s3_path_ to set the location of copied data, _filename_ as the custom prefix of the file and _unload_options_.

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
