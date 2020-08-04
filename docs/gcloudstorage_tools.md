# gcloudstorage_tools
This is the documentation for the gcloudstorage_tools modules and all its contents, with usage examples.

# Index
- [GCloudStorageTool](#gcloudstoragetool)
  - [\_\_init\_\_(self, gs_path=None, bucket=None, subfolder="", filename=None, authenticate=True)](#__init__self-gs_pathnone-bucketnone-subfolder-filenamenone-authenticatetrue)
  - [bucket(self) @property](#bucketself-property)
  - [blob(self) @property](#blobself-property)
  - [set_bucket(self, bucket)](#set_bucketself-bucket)
  - [set_subfolder(self, subfolder)](#set_subfolderself-subfolder)
  - [select_file(self, filename)](#select_fileself-filename)
  - [set_by_path(self, gs_path)](#set_by_pathself-gs_path)
  - [get_gs_path(self)](#get_gs_pathself)
  - [list_all_buckets(self)](#list_all_bucketsself)
  - [get_bucket_info(self, bucket=None)](#get_bucket_infoself-bucketnone)
  - [get_file_info(self, filename=None, info=None)](#get_file_infoself-filenamenone-infonone)
  - [list_contents(self, yield_results=False)](#list_contentsself-yield_resultsfalse)
  - [rename_file(self, new_filename, old_filename)](#rename_fileself-new_filename-old_filename) _(Not Yet Implemented)_
  - [rename_subfolder(self, new_subfolder)](#rename_subfolderself-new_subfolder) _(Not Yet Implemented)_
  - [upload_file(self, filename, remote_path=None)](#upload_fileself-filename-remote_pathnone)
  - [upload_subfolder(self, folder_path)](#upload_subfolderself-folder_path) _(Not Yet Implemented)_
  - [upload_from_dataframe(self, dataframe, file_format='CSV', filename=None, overwrite=False, \*\*kwargs)](#upload_from_dataframeself-dataframe-file_formatcsv-filenamenone-overwritefalse-kwargs)
  - [download_file(self, download_to=None, remote_filename=None, replace=False)](#download_fileself-download_tonone-remote_filenamenone-replacefalse)
  - [download_subfolder(self)](#download_subfolderself) _(Not Yet Implemented)_
  - [download_on_dataframe(self, \*\*kwargs)](#download_on_dataframeself-kwargs)
  - [delete_file(self)](#delete_fileself) _(Not Yet Implemented)_
  - [delete_subfolder(self)](#delete_subfolderself) _(Not Yet Implemented)_

# Module Contents
## GCloudStorageTool
This class handle most of the interaction needed with Google Cloud Storage,
so the base code becomes more readable and straightforward.

### \_\_init\_\_(self, gs_path=None, bucket=None, subfolder="", filename=None, authenticate=True)
Takes a either gs_path or bucket name (and if necessary also subfolder name and file name) as parameters to set the current working directory. It also opens a connection with Google Cloud Storage.

When setting by the gs_path, it will consider that a filename was given if the path doesn't end with a slash, i.e. `/`. If it does, it will consider that the path only has bucket and subfolder arguments. In this implementation, a subfolder **always** end with a slash (`/`).

The paradigm of this class is that all the operations are done in the current working directory, so it is important to set the right path (you can reset it later, but still).

The _authenticate_ parameter set whether the initialization process will use the `fetch_credentials` method or not. This might be desired if the environment is already authenticated, for example in a Google Cloud Composer environment.

Usage example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


# With a filename

gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/example.txt")
# or
gs = GCloudStorageTool(bucket="some_bucket", subfolder="subfolder/", filename="example.txt")


# Without a filename

gs = GCloudStorageTool(gs_path="gs://some_other_bucket/some_subfolder/subpath/")
# or
gs = GCloudStorageTool(bucket="some_other_bucket", subfolder="some_subfolder/subpath/")
```

### bucket(self) @property
Returns the bucket object from the client based on the bucket name given in \_\_init\_\_ or set_bucket.

### blob(self) @property
Returns the blob object from the client based on the filename given in \_\_init\_\_ or select_file. If no filename was given, returns None.

### set_bucket(self, bucket)
Takes a string as a parameter to reset the bucket name and bucket object. It has no return value.

**Warning:** this method doesn't check whether the bucket actually exists or not. This operation may not fail, but other methods and properties might do if the bucket doesn't exist.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")

gs.set_bucket("some_other_bucket")

# Check new path structure
print(gs.get_gs_path())

# output: gs://some_other_bucket/
```

### set_subfolder(self, subfolder)
Takes a string as a parameter to reset the subfolder name. It has no return value.

**Warning:** this method doesn't check whether the subfolder path actually exists or not. This operation may not fail, but other methods and properties might do if the subfolder path doesn't exist.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")

gs.set_subfolder("some/more_complex/subfolder/structure/")

# Check new path structure
print(gs.get_gs_path())

# output: gs://some_bucket/some/more_complex/subfolder/structure/
```

### select_file(self, filename)
Takes a string as a parameter to set or reset the filename name. It has no return value.

**Warning:** this method doesn't check whether the file actually exists or not. This operation may not fail, but other methods and properties might do if the file doesn't exist.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")

gs.select_file("file.csv")

# Check new path structure
print(gs.get_gs_path())

# output: gs://some_bucket/subfolder/file.csv
```

### set_by_path(self, gs_path)
Takes a string as a parameter to reset the bucket name and subfolder name by its GS path. It has no return value.

**Warning:** this method doesn't check whether the given path actually exists or not. This operation may not fail, but other methods and properties might do if the gs path doesn't exist.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")

gs.set_by_path("gs://some_other_bucket/some/more_complex/subfolder/structure/")

# Check new path structure
print(gs.get_gs_path())

# output: gs://some_other_bucket/some/more_complex/subfolder/structure/
```

### get_gs_path(self)
Returns a string containing the GS path for the currently set bucket and subfolder. It takes no parameter.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")

print(gs.get_gs_path())

# output: gs://some_bucket/subfolder/
```

### list_all_buckets(self)
Returns a list of all Buckets in Google Cloud Storage. It takes no parameter.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


# Setting or not a subfolder doesn't change the output of this function
gs = GCloudStorageTool(bucket="some_bucket")

all_buckets = gs.list_all_buckets()

# some code here
```

### get_bucket_info(self, bucket=None)
Returns a dictionary with the information of Name, Datetime Created, Datetime Updated and Owner ID of the currently selected bucket (or the one passed in the parameters).

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(bucket="some_bucket")

bucket_info = gs.get_bucket_info()
print(bucket_info)
```

### get_file_info(self, filename=None, info=None)
Gets the remote file's information.

If no filename is given, it uses the one already set (raises an error if no filename is set).

If an info parameter is given, returns only that info. If not, returns all file's information into a dictionary.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(bucket="some_bucket", subfolder="some_subfolder", filename="file.csv")

remote_file_info = gs.get_file_info()
print(remote_file_info)
```

### list_contents(self, yield_results=False)
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

### rename_file(self, new_filename, old_filename)
Not implemented.

### rename_subfolder(self, new_subfolder)
Not implemented.

### upload_file(self, filename, remote_path=None)
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

### upload_subfolder(self, folder_path)
Not implemented.

### upload_from_dataframe(self, dataframe, file_format='CSV', filename=None, overwrite=False, \*\*kwargs)
Uploads a dataframe directly to a file in the file_format given without having to save the file. If no filename is given, it uses the one set in the blob and will fail if overwrite is set to False.

File formats supported are:
- CSV
- JSON

\*\*kwargs are passed directly to .to_csv or .to_json methods (according with the file format chosen).

The complete documentation of these methods can be found here:
- CSV: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_csv.html
- JSON: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_json.html

Usage Example:
```
import pandas as pd
from instackup.gcloudstorage_tools import GCloudStorageTool


df = pd.read_csv("C:\\Users\\USER\\Desktop\\file.csv")

gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")


gs.upload_from_dataframe(df, file_format="JSON", filename="file.json")

# or

gs.set_blob("gs://some_bucket/subfolder/file.csv")
gs.upload_from_dataframe(df, overwrite=True)
```

### download_file(self, download_to=None, remote_filename=None, replace=False)
Downloads remote gs file to local path.

If download_to parameter is not set, it'll download the file to the current working directory.

If the remote_filename parameter is not set, it will default to the currently set.

If replace is set to True and there is already a file downloaded with the same filename and path, it will replace the file. Otherwise it will raise an error.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


file_location = "gs://some_bucket/other_subfolder/file.csv"

gs = GCloudStorageTool(gs_path=file_location)

# download_file method accepts both options
gs.download_file(download_to="C:\\Users\\USER\\Desktop\\file.csv", remote_filename=file_location)
gs.download_file(download_to="C:\\Users\\USER\\Desktop\\file.csv", replace=True)
```

### download_subfolder(self)
Not implemented.

### download_on_dataframe(self, \*\*kwargs)
Use currently file set information to download file and use it directly on a Pandas DataFrame
without having to save the file.

\*\*kwargs are passed directly to pandas.read_csv method.
The complete documentation of this method can be found here:
https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(gs_path="gs://some_bucket/subfolder/")

# For a well behaved file, you may just use the method directly
gs.select_file("file.csv")
df = gs.download_on_dataframe()

# For a file with a weird layout, you may want to use some parameters to save some time in data treatment
gs.select_file("weird_file.csv")
df = gs.download_on_dataframe(sep=";", encoding="ISO-8859-1", decimal=",")
```

### delete_file(self)
Not implemented.

### delete_subfolder(self)
Not implemented.
