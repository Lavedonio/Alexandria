# s3_tools
This is the documentation for the s3_tools module and all its contents, with usage examples.

# Index
- [S3Tool](#s3tool)
  - [\_\_init\_\_(self, uri=None, bucket=None, subfolder="")](#__init__self-urinone-bucketnone-subfolder)
  - [bucket(self) @property](#bucketself-property)
  - [uri(self) @property](#uriself-property)
  - [set_bucket(self, bucket)](#set_bucketself-bucket)
  - [set_subfolder(self, subfolder)](#set_subfolderself-subfolder)
  - [rename_file(self, old_filename, new_filename)](#rename_fileself-old_filename-new_filename)
  - [rename_subfolder(self, new_subfolder)](#rename_subfolderself-new_subfolder)
  - [list_all_buckets(self)](#list_all_bucketsself)
  - [list_contents(self, yield_results=False)](#list_contentsself-yield_resultsfalse)
  - [upload_file(self, filename, remote_path=None)](#upload_fileself-filename-remote_pathnone)
  - [upload_subfolder(self, folder_path)](#upload_subfolderself-folder_path)
  - [download_file(self, remote_path, filename=None)](#download_fileself-remote_path-filenamenone)
  - [download_subfolder(self, download_to=None)](#download_subfolderself-download_tonone)
  - [delete_file(self, filename, fail_silently=False)](#delete_fileself-filename-fail_silentlyfalse)
  - [delete_subfolder(self)](#delete_subfolderself)

# Module Contents
## S3Tool
This class handle most of the interaction needed with S3, so the base code becomes more readable and straightforward.

To understand the S3 structure, you need to know it is not a hierarchical filesystem, it is only a key-value store, though the key is often used like a file path for organising data, prefix + filename. More information about this can be read in this StackOverFlow thread:
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

A great (not directly related) thread that can help that sink in (and help understand some methods here) is this one: https://stackoverflow.com/questions/35803027/retrieving-subfolders-names-in-s3-bucket-from-boto3

In this class, all keys and keys prefix are being treated as a folder tree structure, since the reason for this to exists is to make the programmers interactions with S3 easier to write and the code easier to read.

### \_\_init\_\_(self, uri=None, bucket=None, subfolder="")
Takes either a _uri_ or both _bucket_ name and _subfolder_ name as parameters to set the current working directory. It also opens a connection with AWS S3.

The paradigm of this class is that all the operations are done in the current working directory, so it is important to set the right path (you can reset it later, but still).

Usage example:
```
from instackup.s3_tools import S3Tool


s3 = S3Tool(uri="s3://some_bucket/subfolder/")

# or

s3 = S3Tool(bucket="some_other_bucket", subfolder="some_subfolder/subpath/")
```

### bucket(self) @property
Returns the bucket object from the client based on the _bucket_name_ attribute. Can be set directly or with \_\_init\_\_ or set_bucket methods.

Usage Example:
```
from instackup.s3_tools import S3Tool


s3 = S3Tool(uri="s3://some_bucket/subfolder/")

# Set a bucket directly
s3.bucket = "some_other_bucket"

# Use the bucket object as needed
print(s3.bucket.objects.all())
```

### uri(self) @property
Returns a string containing the URI for the currently set bucket and subfolder. Can be set directly or with \_\_init\_\_ method.

Usage Example:
```
from instackup.s3_tools import S3Tool


s3 = S3Tool(bucket="some_bucket", subfolder="subfolder/")

# Set a uri directly
s3.uri = "s3://some_other_bucket/some/more_complex/subfolder/structure/"

# Use the uri as needed
print(s3.uri)
```

### set_bucket(self, bucket)
Takes a string as a parameter to reset the _bucket_ name, its bucket object and the _subfolder_. It has no return value.

Usage Example:
```
from instackup.s3_tools import S3Tool


s3 = S3Tool(uri="s3://some_bucket/subfolder/")

s3.set_bucket("some_other_bucket")

# Check new path structure
print(s3.uri)
```

### set_subfolder(self, subfolder)
Takes a string as the parameter to reset the _subfolder_ name. It has no return value.

Usage Example:
```
from instackup.s3_tools import S3Tool


s3 = S3Tool(uri="s3://some_bucket/subfolder/")

s3.set_subfolder("some/more_complex/subfolder/structure/")

# Check new path structure
print(s3.uri)
```

### rename_file(self, old_filename, new_filename)
Takes 2 strings containing file names and rename only the filename from path key, so the final result is similar to rename a file. It has no return value.

Usage Example:
```
from instackup.s3_tools import S3Tool


s3 = S3Tool(bucket="some_bucket", subfolder="subfolder/")

s3.rename_file("old_name.csv", "new_name.csv")
```

### rename_subfolder(self, new_subfolder)
Takes a string containing the _new subfolder_ name and renames all keys in the currently set path, so the final result is similar to rename a subfolder. It has no return value.

Usage Example:
```
from instackup.s3_tools import S3Tool


old_subfolder = "some/more_complex/subfolder/structure/"
new_subfolder = "some/new/subfolder/structure/"

s3 = S3Tool(bucket="some_bucket", subfolder=old_subfolder)

# The final result is similar to just rename the "more_complex" folder to "new"
s3.rename_subfolder(new_subfolder)
```

### list_all_buckets(self)
Returns a list of all buckets in S3. It takes no parameter.

Usage Example:
```
from instackup.s3_tools import S3Tool


# Setting or not a subfolder doesn't change the output of this function
s3 = S3Tool(bucket="some_bucket")

all_buckets = s3.list_all_buckets()

# some code here
```

### list_contents(self, yield_results=False)
Lists all files that correspond with bucket and subfolder set at the initialization.

It can either return a list or yield a generator. Lists can be more familiar to use, but when dealing with large amounts of data, yielding the results may be a better option in terms of efficiency.

For more information on how to use generators and yield, check this video:
https://www.youtube.com/watch?v=bD05uGo_sVI

Usage Example:
```
from instackup.s3_tools import S3Tool


s3 = S3Tool(uri="s3://some_bucket/subfolder/")

path_contents = s3.list_contents()

if len(path_contents) == 0:
    s3.set_subfolder("logs/subfolder/")

    # When a specific bucket/ bucket + subfolder contains a lot of data,
    # that's when yielding the results may be more efficient.
    for file in s3.list_contents(yield_results=True):
        # Do something

# some code here
```

### upload_file(self, filename, remote_path=None)
Uploads file to remote path in S3.

_remote_path_ can take either the URI or a subfolder only one. It has no return value.

If the _remote_path_ parameter is not set, it will default to whatever subfolder is set in instance of the class plus the _file name_ that is being uploaded.

Usage Example:
```
from instackup.s3_tools import S3Tool


file_location = "C:\\Users\\USER\\Desktop\\file.csv"

s3 = S3Tool(uri="s3://some_bucket/subfolder/")

# upload_file method accepts all 3 options
s3.upload_file(file_location)
s3.upload_file(file_location, "s3://some_bucket/other_subfolder/")
s3.upload_file(file_location, "another_subfolder/")  # Just subfolder
```

### upload_subfolder(self, folder_path)
Uploads a local folder to with prefix as currently set enviroment (bucket and subfolder).

Keeps folder structure as prefix in S3.

Behaves as if it was downloading an entire folder to current path.

Usage Example:
```
from instackup.s3_tools import S3Tool


folder = "C:\\Users\\USER\\Documents\\some_folder"

s3 = S3Tool(uri="s3://some_bucket/subfolder/")

s3.upload_file(folder)
# folder contents will be in URI "s3://some_bucket/subfolder/some_folder"
```

### download_file(self, remote_path, filename=None)
Downloads remote S3 file to local path.

_remote_path_ can take either the URI or a subfolder only one. It has no return value.

If the _filename_ parameter is not set, it will default to whatever subfolder is set in instance of the class plus the file name that is being downloaded.

Usage Example:
```
from instackup.s3_tools import S3Tool


file_desired_location = "C:\\Users\\USER\\Desktop\\file.csv"
remote_location = "s3://some_bucket/other_subfolder/file.csv"

s3 = S3Tool(uri="s3://some_bucket/subfolder/")

# download_file method accepts both options
s3.download_file(remote_location)
s3.download_file(remote_location, file_desired_location)
```

### download_subfolder(self, download_to=None)
Downloads remote S3 files in currently set enviroment (bucket and subfolder) to current (or defined in download_to parameter) location.

Behaves as if it was downloading an entire folder to current path.

Usage Example:
```
from instackup.s3_tools import S3Tool


desired_location = "C:\\Users\\USER\\Desktop\\downloaded_files"

s3 = S3Tool(uri="s3://some_bucket/subfolder/")

s3.download_file(download_to=desired_location)
```

### delete_file(self, filename, fail_silently=False)
Deletes file from currently set path. It has no return value.

Raises an error if file doesn't exist and _fail_silently_ parameter is set to False.

Usage Example:
```
from instackup.s3_tools import S3Tool


filename = "file.csv"

s3 = S3Tool(uri="s3://some_bucket/subfolder/")

s3.delete_file(filename)

# Will fail to delete the same file it was deleted before,
# but won't raise any error due to fail_silently being set to True
s3.delete_file(filename, fail_silently=True)
```

### delete_subfolder(self)
Deletes all files with subfolder prefix, so the final result is similar to deleting a subfolder. It has no return value.

Once the subfolder is deleted, it resets to no extra path (empty subfolder name).

Usage Example:
```
from instackup.s3_tools import S3Tool


filename = "file.csv"

s3 = S3Tool(uri="s3://some_bucket/subfolder/")

s3.delete_folder()

# Check new path structure
print(s3.uri)
```
