# postgresql_tools
This is the documentation for the postgresql_tools modules and all its contents, with usage examples.

# Index
- [PostgreSQLTool](#postgresqltool)
  - [\_\_init\_\_(self, connection='default')](#__init__self-connectiondefault)
  - [connect(self, fail_silently=False)](#connectself-fail_silentlyfalse)
  - [commit(self)](#commitself)
  - [rollback(self)](#rollbackself)
  - [close_connection(self)](#close_connectionself)
  - [execute_sql(self, command, fail_silently=False)](#execute_sqlself-command-fail_silentlyfalse)
  - [query(self, sql_query, fetch_through_pandas=True, fail_silently=False)](#queryself-sql_query-fetch_through_pandastrue-fail_silentlyfalse)
  - [describe_table(self, table, schema="public", fetch_through_pandas=True, fail_silently=False)](#describe_tableself-table-schemapublic-fetch_through_pandastrue-fail_silentlyfalse)
  - [get_all_db_info(self, get_json_info=True, fetch_through_pandas=True, fail_silently=False)](#get_all_db_infoself-get_json_infotrue-fetch_through_pandastrue-fail_silentlyfalse)

# Module Contents
## PostgreSQLTool
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

### \_\_init\_\_(self, connection='default')
Initialization takes connection parameter that select which connection to use. It has no return value.

The \_\_init\_\_ method doesn't actually opens the connection, but sets all values required by the connect method.

Usage example:
```
from instackup.postgresql_tools import PostgreSQLTool

pg = PostgreSQLTool()
```

### connect(self, fail_silently=False)
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

### commit(self)
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

### rollback(self)
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

### close_connection(self)
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

### execute_sql(self, command, fail_silently=False)
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

### query(self, sql_query, fetch_through_pandas=True, fail_silently=False)
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

### describe_table(self, table, schema="public", fetch_through_pandas=True, fail_silently=False)
Special query that returns all metadata from a specific table

Usage example:
```
from instackup.postgresql_tools import PostgreSQLTool


pg = PostgreSQLTool()
pg.connect()

try:
    # Returns a list of tuples containing the rows of the response (Table: public.users)
    table = pg.describe_table("users", fetch_through_pandas=False, fail_silently=True)

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

    # Returns a Pandas dataframe with all schema info of that specific schema.table
    # To do operations with dataframe, you'll need to import pandas library
    df = pg.describe_table("airflow_logs", schema="another_schema")

    # other code
```

### get_all_db_info(self, get_json_info=True, fetch_through_pandas=True, fail_silently=False)
Gets all Database info, using a INFORMATION_SCHEMA query.

Ignore table pg_stat_statements and tables inside schemas pg_catalog and information_schema.

If get_json_info parameter is True, it adds 2 columns to add the data types from each key inside json and jsonb columns.

fetch_through_pandas and fail_silently parameters are passed directly to the query method if get_json_info parameter is set to False; if it's not, these 2 parameters are passed as their default values.

Returns either a Dataframe if get_json_info or fetch_through_pandas parameters are set to True, or a list of tuples, each representing a row, with their position in the same order as in the columns of the INFORMATION_SCHEMA.COLUMNS table.

Usage example:
```
from instackup.postgresql_tools import PostgreSQLTool


pg = PostgreSQLTool()
pg.connect()

try:
    # Returns a list of tuples containing the rows of the response
    schema_info = pg.get_all_db_info(get_json_info=False, fetch_through_pandas=False, fail_silently=True)

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

    # Returns a Pandas dataframe with all schema info, including inside JSON and JSONB fields
    # To do operations with dataframe, you'll need to import pandas library
    df = pg.get_all_db_info()

    # other code
```
