# gcloudstorage_tools
This is the documentation for the gcloudstorage_tools module and all its contents, with usage examples.

# Index
- [GCloudStorageTool](#gcloudstoragetool)
  - [\_\_init\_\_(self, uri=None, bucket=None, subfolder="", filename=None, authenticate=True)](#__init__self-urinone-bucketnone-subfolder-filenamenone-authenticatetrue)
  - [bucket(self) @property](#bucketself-property)
  - [blob(self) @property](#blobself-property)
  - [uri(self) @property](#uriself-property)
  - [set_bucket(self, bucket)](#set_bucketself-bucket)
  - [set_subfolder(self, subfolder)](#set_subfolderself-subfolder)
  - [select_file(self, filename)](#select_fileself-filename)
  - [list_all_buckets(self)](#list_all_bucketsself)
  - [get_bucket_info(self, bucket=None)](#get_bucket_infoself-bucketnone)
  - [get_file_info(self, filename=None, info=None)](#get_file_infoself-filenamenone-infonone)
  - [list_contents(self, yield_results=False)](#list_contentsself-yield_resultsfalse)
  - [rename_file(self, new_filename)](#rename_fileself-new_filename)
  - [rename_subfolder(self, new_subfolder)](#rename_subfolderself-new_subfolder)
  - [upload_file(self, filename, remote_path=None)](#upload_fileself-filename-remote_pathnone)
  - [upload_subfolder(self, folder_path)](#upload_subfolderself-folder_path)
  - [upload_from_dataframe(self, dataframe, file_format='CSV', filename=None, overwrite=False, \*\*kwargs)](#upload_from_dataframeself-dataframe-file_formatcsv-filenamenone-overwritefalse-kwargs)
  - [download_file(self, download_to=None, remote_filename=None, replace=False)](#download_fileself-download_tonone-remote_filenamenone-replacefalse)
  - [download_subfolder(self, download_to=None)](#download_subfolderself-download_tonone)
  - [download_on_dataframe(self, \*\*kwargs)](#download_on_dataframeself-kwargs)
  - [download_as_string(self, remote_filename=None, encoding="UTF-8")](#download_as_stringself-remote_filenamenone-encodingutf-8)
  - [delete_file(self)](#delete_fileself)
  - [delete_subfolder(self)](#delete_subfolderself)

# Module Contents
## GCloudStorageTool
This class handle most of the interaction needed with Google Cloud Storage, so the base code becomes more readable and straightforward.

### \_\_init\_\_(self, uri=None, bucket=None, subfolder="", filename=None, authenticate=True)
Takes a either _uri_ or _bucket_ name (and if necessary also _subfolder_ name and _file name_) as parameters to set the current working directory. It also opens a connection with Google Cloud Storage.

When setting by the _uri_, it will consider that a filename was given if the path doesn't end with a slash, i.e. `/`. If it does, it will consider that the path only has bucket and subfolder arguments. In this implementation, a subfolder **always** end with a slash (`/`).

The paradigm of this class is that all the operations are done in the current working directory, so it is important to set the right path (you can reset it later, but still).

The _authenticate_ parameter set whether the initialization process will use the `fetch_credentials` method or not. This might be desired if the environment is already authenticated, for example in a Google Cloud Composer environment.

Usage example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


# With a filename

gs = GCloudStorageTool(uri="gs://some_bucket/subfolder/example.txt")
# or
gs = GCloudStorageTool(bucket="some_bucket", subfolder="subfolder/", filename="example.txt")


# Without a filename

gs = GCloudStorageTool(uri="gs://some_other_bucket/some_subfolder/subpath/")
# or
gs = GCloudStorageTool(bucket="some_other_bucket", subfolder="some_subfolder/subpath/")
```

### bucket(self) @property
Returns the bucket object from the client based on the _bucket_name_ attribute. Can be set directly or with \_\_init\_\_ or set_bucket methods.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(uri="gs://some_bucket/subfolder/file.csv")

# Set a bucket directly
gs.bucket = "some_other_bucket"

# Use the bucket object as needed
gs.bucket.blob("subfolder/file.csv").download_to_filename()
```

### blob(self) @property
Returns the blob object from the client based on the _subfolder_ and _filename_ attributes. Can be set directly or with \_\_init\_\_ or select_file methods. If no _filename_ was given in \_\_init\_\_, returns None.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(bucket="some_bucket")

# Set a blob directly
gs.blob = "subfolder/file.csv"

# Use the blob object as needed
gs.blob.download_to_filename()
```

### uri(self) @property
Returns a string containing the URI for the currently set bucket, subfolder and filename. Can be set directly or with \_\_init\_\_ method.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(bucket="some_bucket")

# Set a uri directly
gs.uri = "gs://some_other_bucket/subfolder/file.csv"

# Use the uri as needed
print(gs.uri)
```

### set_bucket(self, bucket)
Takes a string as a parameter to reset the _bucket_ name and bucket object. It has no return value.

This method also resets the _subfolder_ and _filename_ attributes.

**Warning:** this method doesn't check whether the bucket actually exists or not. This operation may not fail, but other methods and properties might do if the bucket doesn't exist.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(uri="gs://some_bucket/subfolder/file.csv")

# Note that it'll reset the subfolder and filename
gs.set_bucket("some_other_bucket")

# Check new path structure
print(gs.uri)

# output: gs://some_other_bucket/
```

### set_subfolder(self, subfolder)
Takes a string as the parameter to reset the _subfolder_ name. It has no return value.

This method also resets the _filename_ attribute.

**Warning:** this method doesn't check whether the subfolder path actually exists or not. This operation may not fail, but other methods and properties might do if the subfolder path doesn't exist.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(uri="gs://some_bucket/subfolder/file.csv")

# Note that it'll reset the filename
gs.set_subfolder("some/more_complex/subfolder/structure/")

# Check new path structure
print(gs.uri)

# output: gs://some_bucket/some/more_complex/subfolder/structure/
```

### select_file(self, filename)
Takes a string as the parameter to set or reset the _filename_. It has no return value.

**Warning:** this method doesn't check whether the file actually exists or not. This operation may not fail, but other methods and properties might do if the file doesn't exist.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(uri="gs://some_bucket/subfolder/")

gs.select_file("file.csv")

# Check new path structure
print(gs.uri)

# output: gs://some_bucket/subfolder/file.csv
```

### list_all_buckets(self)
Returns a list of all buckets in Google Cloud Storage. It takes no parameter.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


# Setting or not a subfolder doesn't change the output of this function
gs = GCloudStorageTool(bucket="some_bucket")

all_buckets = gs.list_all_buckets()

# some code here
```

### get_bucket_info(self, bucket=None)
Returns a dictionary with the information of the currently selected _bucket_ (or the one passed in the parameters).

The fields contained in the returned dictionary are:
- Name
- TimeCreated
- TimeUpdated
- OwnerID

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(bucket="some_bucket")

bucket_info = gs.get_bucket_info()
print(bucket_info)
```

### get_file_info(self, filename=None, info=None)
Gets the remote file's information.

If no _filename_ is given, it uses the one already set (raises an error if no filename is set).

If an _info_ parameter is given, returns only that info. If not, returns all file's information into a dictionary.

The fields contained in the returned dictionary (and available) are:
- Name
- Bucket
- ContentType
- TimeCreated
- TimeUpdated
- TimeDeleted
- Size
- MD5
- OwnerID
- CRC32c
- EncryptionAlgorithm
- EncryptionKeySHA256

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(bucket="some_bucket", subfolder="some_subfolder", filename="file.csv")

remote_file_info = gs.get_file_info()
print(remote_file_info)
```

### list_contents(self, yield_results=False)
Lists all files that correspond with _bucket_ and _subfolder_ set at the initialization.

It can either return a list or yield a generator. Lists can be more familiar to use, but when dealing with large amounts of data, yielding the results may be a better option in terms of efficiency.

For more information on how to use generators and yield, check this video:
https://www.youtube.com/watch?v=bD05uGo_sVI

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(uri="gs://some_bucket/subfolder/")

path_contents = gs.list_contents()

if len(path_contents) == 0:
    gs.set_subfolder("logs/subfolder/")

    # When a specific bucket/ bucket + subfolder contains a lot of data,
    # that's when yielding the results may be more efficient.
    for file in gs.list_contents(yield_results=True):
        # Do something

# some code here
```

### rename_file(self, new_filename)
Rename only last part of key path, so the final result is similar to rename a file.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(uri="gs://some_bucket/subfolder/old_filename.json")

# Renames "old_filename.json" to "new_filename.json"
gs.rename_file("new_filename.json")

print(gs.uri)
# output: gs://some_bucket/subfolder/new_filename.json
```

### rename_subfolder(self, new_subfolder)
Renames all keys that match the current set subfolder, so the final result is similar to rename a subfolder.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(bucket="some_bucket", subfolder="a_generic_subfolder/", filename="filename.json")

# Renames subfolder from "a_generic_subfolder/" to "another_generic_subfolder/" and resets the filename.
gs.rename_subfolder("another_generic_subfolder")

print(gs.uri)
# output: gs://some_bucket/another_generic_subfolder/filename.json
```

### upload_file(self, filename, remote_path=None)
Uploads file to remote path in Google Cloud Storage (GS).

_remote_path_ can take either a full GS path or a subfolder only one.

If the _remote_path_ parameter is not set, it will default to whatever subfolder is set in instance of the class plus the file name that is being uploaded.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


file_location = "C:\\Users\\USER\\Desktop\\file.csv"

gs = GCloudStorageTool(uri="gs://some_bucket/subfolder/")

# upload_file method accepts all 3 options
gs.upload_file(file_location)
gs.upload_file(file_location, "gs://some_bucket/other_subfolder/")
gs.upload_file(file_location, "another_subfolder/")  # Just subfolder
```

### upload_subfolder(self, folder_path)
Uploads a local folder to with prefix as currently set enviroment (bucket and subfolder).

Keeps folder structure as prefix in Google Cloud Storage.

Behaves as if it was downloading an entire folder to current path.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


folder = "C:\\Users\\USER\\Documents\\some_folder"

gs = GCloudStorageTool(uri="gs://some_bucket/subfolder/")

gs.upload_subfolder(folder)
# folder contents will be in URI "gs://some_bucket/subfolder/some_folder"
```

### upload_from_dataframe(self, dataframe, file_format='CSV', filename=None, overwrite=False, \*\*kwargs)
Uploads a _dataframe_ directly to a file in the _file_format_ given without having to save the file. If no _filename_ is given, it uses the one set in the blob and will fail if _overwrite_ is set to False.

File formats supported are:
- CSV
- JSON

_\*\*kwargs_ are passed directly to pandas.to_csv or pandas.to_json methods (according with the file format chosen).

The complete documentation of these methods can be found here:
- CSV: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_csv.html
- JSON: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_json.html

Usage Example:
```
import pandas as pd
from instackup.gcloudstorage_tools import GCloudStorageTool


df = pd.read_csv("C:\\Users\\USER\\Desktop\\file.csv")

gs = GCloudStorageTool(uri="gs://some_bucket/subfolder/")


gs.upload_from_dataframe(df, file_format="JSON", filename="file.json")

# or

gs.uri = "gs://some_bucket/subfolder/file.csv"
gs.upload_from_dataframe(df, overwrite=True)
```

### download_file(self, download_to=None, remote_filename=None, replace=False)
Downloads remote gs file to local path.

If _download_to_ parameter is not set, it'll download the file to the current working directory.

If the _remote_filename_ parameter is not set, it will default to the currently set.

If _replace_ is set to True and there is already a file downloaded with the same filename and path, it will replace the file. Otherwise it will raise an error.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


file_location = "gs://some_bucket/other_subfolder/file.csv"

gs = GCloudStorageTool(uri=file_location)

# download_file method accepts both options
gs.download_file(download_to="C:\\Users\\USER\\Desktop\\file.csv", remote_filename=file_location)
gs.download_file(download_to="C:\\Users\\USER\\Desktop\\file.csv", replace=True)
```

### download_subfolder(self, download_to=None)
Downloads remote Storage files in currently set enviroment (bucket and subfolder) to current (or defined in download_to parameter) location.

Behaves as if it was downloading an entire folder to current path.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


desired_location = "C:\\Users\\USER\\Desktop\\downloaded_files"

gs = GCloudStorageTool(bucket="some_bucket", subfolder="some_subfolder/")

gs.download_subfolder(download_to=desired_location)
```

### download_on_dataframe(self, \*\*kwargs)
Use currently file set information to download file and use it directly on a Pandas DataFrame without having to save the file.

_\*\*kwargs_ are passed directly to pandas.read_csv method.

The complete documentation of this method can be found here:
https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(uri="gs://some_bucket/subfolder/")

# For a well behaved file, you may just use the method directly
gs.select_file("file.csv")
df = gs.download_on_dataframe()

# For a file with a weird layout, you may want to use some parameters to save some time in data treatment
gs.select_file("weird_file.csv")
df = gs.download_on_dataframe(sep=";", encoding="ISO-8859-1", decimal=",")
```

### download_as_string(self, remote_filename=None, encoding="UTF-8")
Downloads a remote object directly into a Python string, avoiding it to have to be saved.

Usage Example:
```
import json
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(uri="gs://some_bucket/subfolder/")
gs.select_file("file.json")

# Getting the file in a string format
file_string = gs.download_as_string()

# If its a JSON file, for example, you can pass the result to a json.load function
py_dict = json.loads(file_string)
```

### delete_file(self)
Deletes the selected file from Google Cloud Storage.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(bucket="some_bucket", subfolder="some/subfolder/structure/", filename="file.csv")

# Delete file and reset filename
gs.delete_file()

print(gs.uri)
# output: gs://some_bucket/some/subfolder/structure/
```

### delete_subfolder(self)
Deletes all files with subfolder prefix, so the final result is similar to deleting a subfolder.

Usage Example:
```
from instackup.gcloudstorage_tools import GCloudStorageTool


gs = GCloudStorageTool(bucket="some_bucket", subfolder="some/subfolder/structure/")

# Delete subfolder and reset filename and subfolder name
gs.delete_subfolder()

print(gs.uri)
# output: gs://some_bucket/
```
