# sql_tools
This is the documentation for the sql_tools module and all its contents, with usage examples.

# Index
- [SQLTool](#sqltool)
  - [\_\_init\_\_(self, sql_type, filename=None, connection='default')](#__init__self-sql_type-filenamenone-connectiondefault)
  - [connect(self, fail_silently=False)](#connectself-fail_silentlyfalse)
  - [commit(self)](#commitself)
  - [rollback(self)](#rollbackself)
  - [close_connection(self)](#close_connectionself)
  - [execute_sql(self, command, fail_silently=False)](#execute_sqlself-command-fail_silentlyfalse)
  - [query(self, sql_query, fetch_through_pandas=True, fail_silently=False)](#queryself-sql_query-fetch_through_pandastrue-fail_silentlyfalse)
- [SQLiteTool](#sqlitetool)
  - [\_\_init\_\_(self, filename=None)](#__init__self-filenamenone)
  - [describe_table(self, table, fetch_through_pandas=True, fail_silently=False)](#describe_tableself-table-fetch_through_pandastrue-fail_silentlyfalse)
- [MySQLTool](#mysqltool)
  - [\_\_init\_\_(self, connection='default')](#__init__self-connectiondefault)
  - [describe_table(self, table, fetch_through_pandas=True, fail_silently=False)](#describe_tableself-table-fetch_through_pandastrue-fail_silentlyfalse-1)
- [PostgreSQLTool](#postgresqltool)
  - [\_\_init\_\_(self, connection='default')](#__init__self-connectiondefault-1)
  - [describe_table(self, table, schema="public", fetch_through_pandas=True, fail_silently=False)](#describe_tableself-table-schemapublic-fetch_through_pandastrue-fail_silentlyfalse-2)
  - [get_all_db_info(self, get_json_info=True, fetch_through_pandas=True, fail_silently=False)](#get_all_db_infoself-get_json_infotrue-fetch_through_pandastrue-fail_silentlyfalse)

# Module Contents
## SQLTool
This class a base class for the different types of SQL databases. Other classes in this module ([SQLiteTool](#sqlitetool) and [PostgreSQLTool](#postgresqltool)) builds upon these attributes and methods.

This class implements the with statement, so there are 2 ways of using it.

**1st way:**

```
from instackup.sql_tools import SQLTool

with SQLTool("SQLite") as db:
    # use db object to interact with a database
```

**2nd way:**

```
from instackup.sql_tools import SQLTool

db = SQLTool("SQLite")
db.connect()

try:
    # use db object to interact with a database
except Exception as e:
    db.rollback()
    raise e
else:
    db.commit()
finally:
    db.close_connection()
```

Easy to see that it is recommended (and easier) to use the first syntax.

### \_\_init\_\_(self, sql_type, filename=None, connection='default')
Initialization takes _sql_type_ parameter, which sets the kind of database it's going to access, _filename_ parameter, which is only used if the sql_type is "SQLite", and _connection_ parameter, that select which connection to use.

It has no return value.

The \_\_init\_\_ method doesn't actually opens the connection, but sets all values required by the connect method.

Usage example:
```
from instackup.sql_tools import SQLTool

db = SQLTool("SQLite")
```

### connect(self, fail_silently=False)
Create the connection using the \_\_init\_\_ attributes and returns its own object for with statement.

If _fail_silently_ parameter is set to True, any errors will be surpressed and not stop the code execution.

Usage example:
```
from instackup.sql_tools import SQLTool

db = SQLTool("SQLite")
db.connect()
# remember to close the connection later

# or

with SQLTool("PostgreSQL") as db:
    # Already connected, use db object in this context

```

### commit(self)
Commits any pending transaction to the database. It has no extra parameter or return value.

Usage example:
```
from instackup.sql_tools import SQLTool

db = SQLTool("PostgreSQL")
db.connect()
# Do stuff
db.commit()
# remember to close the connection later

# or

with SQLTool("SQLite") as db:
    # Already connected, use db object in this context

    # Do stuff

    # No need to explictly commit as it will do when leaving this context, but nonetheless:
    db.commit()
```

### rollback(self)
Roll back to the start of any pending transaction. It has no extra parameter or return value.

Usage example:
```
from instackup.sql_tools import SQLTool

db = SQLTool("SQLite")
db.connect()

try:
    # Do stuff
except Exception as e:
    db.rollback()
    raise e
else:
    db.commit()
finally:
    # remember to close the connection later
    db.close_connection()

# or

with SQLTool("PostgreSQL") as db:
    # Already connected, use db object in this context

    # Do stuff
    
    # No need to explictly commit or rollback as it will do when leaving this context, but nonetheless:
    if meet_condition:
        db.commit()
    else:
        db.rollback()
```

### close_connection(self)
Closes Connection with the database. It has no extra parameter or return value.

Usage example:
```
from instackup.sql_tools import SQLTool

db = SQLTool("PostgreSQL")
db.connect()

try:
    # Do stuff
except Exception as e:
    db.rollback()
    raise e
else:
    db.commit()
finally:
    db.close_connection()

# or

with SQLTool("SQLite") as db:
    # Already connected, use db object in this context

    # Do stuff

    # Will close the connection automatically when existing this scope
```

### execute_sql(self, command, fail_silently=False)
Execute a SQL _command_ (CREATE, UPDATE and DROP). It has no return value.

If _fail_silently_ parameter is set to True, any errors will be surpressed and not stop the code execution.

Usage example:
```
from instackup.sql_tools import SQLTool


sql_cmd = """CREATE TABLE test (
    id          integer NOT NULL CONSTRAINT firstkey PRIMARY KEY,
    username    varchar(40) UNIQUE NOT NULL,
    fullname    varchar(64) NOT NULL,
    created_at  TIMESTAMP NOT NULL,
    last_login  TIMESTAMP
);
"""


db = SQLTool("PostgreSQL")
db.connect()

try:
    # Execute the command
    db.execute_sql(sql_cmd)

except Exception as e:
    db.rollback()
    raise e
else:
    db.commit()
finally:
    # remember to close the connection later
    db.close_connection()

# or

with SQLTool("PostgreSQL") as db:
    # Already connected, use db object in this context

    # This command would throw an error (since the table already was created before),
    # but since fail_silently parameter is set to True, it'll catch the exception
    # and let the code continue past this point.
    db.execute_sql(sql_cmd, fail_silently=True)

    # other code
```

### query(self, sql_query, fetch_through_pandas=True, fail_silently=False)
Run a query and return the results.

_fetch_through_pandas_ parameter tells if the query should be parsed by the cursor or pandas.

If _fail_silently_ parameter is set to True, any errors will be surpressed and not stop the code execution.

Usage example:
```
from instackup.sql_tools import SQLTool


sql_query = """SELECT * FROM table LIMIT 100"""


db = SQLTool("PostgreSQL")
db.connect()

try:
    # Returns a list of tuples containing the rows of the response
    table = db.query(sql_cmd, fetch_through_pandas=False, fail_silently=True)

    # Do something with table variable

except Exception as e:
    db.rollback()
    raise e
else:
    db.commit()
finally:
    # remember to close the connection later
    db.close_connection()

# or

with SQLTool("SQLite") as db:
    # Already connected, use db object in this context

    # Returns a Pandas dataframe
    df = db.query(sql_cmd)

    # To do operations with dataframe, you'll need to import pandas library

    # other code
```

## SQLiteTool
This class handle most of the interaction needed with SQLite3 databases, so the base code becomes more readable and straightforward. This class inherits from [SQLTool](#sqltool), so its attributes and methods can (and will) be accessed from this class. Read the documentation of the base class for more info.

This class implements the with statement, so there are 2 ways of using it.

**1st way:**

```
from instackup.sql_tools import SQLiteTool

with SQLiteTool() as sl:
    # use sl object to interact with PostgreSQL database
```

**2nd way:**

```
from instackup.sql_tools import SQLiteTool

sl = SQLiteTool()
sl.connect()

try:
    # use sl object to interact with PostgreSQL database
except Exception as e:
    sl.rollback()
    raise e
else:
    sl.commit()
finally:
    sl.close_connection()
```

Easy to see that it is recommended (and easier) to use the first syntax.

### \_\_init\_\_(self, filename=None)
Initialization takes the _filename_ parameter, that selects which SQLite3 database file to use; if it's not set, creates an temporary in-memory database. It has no return value.

The \_\_init\_\_ method doesn't actually opens the connection, but sets all values required by the connect method.

Usage example:
```
from instackup.sql_tools import SQLiteTool

sl = SQLiteTool(filename='db.sqlite3')
```

### describe_table(self, table, fetch_through_pandas=True, fail_silently=False)
Special query that returns all metadata from a specific _table_.

Usage example:
```
from instackup.sql_tools import SQLiteTool


sl = SQLiteTool()  # In-memory sqlite database
sl.connect()

try:
    # Returns a list of tuples containing the rows of the response
    table = sl.describe_table("users", fetch_through_pandas=False, fail_silently=True)

    # Do something with table variable

except Exception as e:
    sl.rollback()
    raise e
else:
    sl.commit()
finally:
    # remember to close the connection later
    sl.close_connection()

# or

with SQLiteTool() as sl:
    # Already connected, use sl object in this context

    # Returns a Pandas dataframe with all schema info of that specific table
    # To do operations with dataframe, you'll need to import pandas library
    df = sl.describe_table("airflow_logs")

    # other code
```

## MySQLTool
This class handle most of the interaction needed with PostgreSQL databases, so the base code becomes more readable and straightforward. This class inherits from [SQLTool](#sqltool), so its attributes and methods can (and will) be accessed from this class. Read the documentation of the base class for more info.

This class implements the with statement, so there are 2 ways of using it.

**1st way:**

```
from instackup.sql_tools import MySQLTool

with MySQLTool() as my:
    # use my object to interact with PostgreSQL database
```

**2nd way:**

```
from instackup.sql_tools import MySQLTool

my = MySQLTool()
my.connect()

try:
    # use my object to interact with PostgreSQL database
except Exception as e:
    my.rollback()
    raise e
else:
    my.commit()
finally:
    my.close_connection()
```

Easy to see that it is recommended (and easier) to use the first syntax.

### \_\_init\_\_(self, connection='default')
Initialization takes _connection_ parameter, that selects which connection to use. It has no return value.

The \_\_init\_\_ method doesn't actually opens the connection, but sets all values required by the connect method.

Usage example:
```
from instackup.sql_tools import MySQLTool

my = MySQLTool(connection='default')
```

### describe_table(self, table, fetch_through_pandas=True, fail_silently=False)
Returns all metadata from a specific table.

Usage example:
```
from instackup.sql_tools import MySQLTool


my = MySQLTool()
my.connect()

try:
    # Returns a list of tuples containing the rows of the response
    table = my.describe_table("users", fetch_through_pandas=False, fail_silently=True)

    # Do something with table variable

except Exception as e:
    my.rollback()
    raise e
else:
    my.commit()
finally:
    # remember to close the connection later
    my.close_connection()

# or

with MySQLTool() as my:
    # Already connected, use my object in this context

    # Returns a Pandas dataframe with all schema info of that specific schema.table
    # To do operations with dataframe, you'll need to import pandas library
    df = my.describe_table("airflow_logs")

    # other code
```

## PostgreSQLTool
This class handle most of the interaction needed with PostgreSQL databases, so the base code becomes more readable and straightforward. This class inherits from [SQLTool](#sqltool), so its attributes and methods can (and will) be accessed from this class. Read the documentation of the base class for more info.

This class implements the with statement, so there are 2 ways of using it.

**1st way:**

```
from instackup.sql_tools import PostgreSQLTool

with PostgreSQLTool() as pg:
    # use pg object to interact with PostgreSQL database
```

**2nd way:**

```
from instackup.sql_tools import PostgreSQLTool

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
Initialization takes _connection_ parameter, that selects which connection to use. It has no return value.

The \_\_init\_\_ method doesn't actually opens the connection, but sets all values required by the connect method.

Usage example:
```
from instackup.sql_tools import PostgreSQLTool

pg = PostgreSQLTool(connection='default')
```

### describe_table(self, table, schema="public", fetch_through_pandas=True, fail_silently=False)
Special query that returns all metadata from a specific table.

Usage example:
```
from instackup.sql_tools import PostgreSQLTool


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

If _get_json_info_ parameter is True, it adds 2 columns with the data types from each key inside json and jsonb columns.

_fetch_through_pandas_ and _fail_silently_ parameters are passed directly to the _query_ method if _get_json_info_ parameter is set to False; if it's not, these 2 parameters are passed as their default values.

Returns a DataFrame if either _get_json_info_ or _fetch_through_pandas_ parameters are set to True; otherwise returns a list of tuples, each representing a row, with their position in the same order as in the columns of the INFORMATION_SCHEMA.COLUMNS table.

Usage example:
```
from instackup.sql_tools import PostgreSQLTool


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
