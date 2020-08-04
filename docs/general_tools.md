# general_tools
This is the documentation for the general_tools modules and all its contents, with usage examples.

# Index
- [fetch_credentials(service_name, \*\*kwargs)](#fetch_credentialsservice_name-kwargs)
- [code_location()](#code_location)
- [unicode_to_ascii(unicode_string)](#unicode_to_asciiunicode_string)
- [parse_remote_uri(uri, service)](#parse_remote_uriuri-service)

# Module Contents
## fetch_credentials(service_name, \*\*kwargs)
Gets the credentials from the secret file set in `CREDENTIALS_HOME` variable and returns the credentials of the selected service in a dictionary. If service is "credentials_path", a path is returned instead.

It's mainly meant to be used by the other modules, but it can be used to retrieve other credentials in order to stardardize the local and remote code execution.

Usage example:
```
from instackup.general_tools import fetch_credentials

# Using just a service name
print(fetch_credentials(service_name="Google"))
print(fetch_credentials("AWS"))

# Getting only one db connection
print(fetch_credentials("RedShift", connection_type="cluster_credentials"))
print(fetch_credentials(service_name="PostgreSQL", connection="default"))

# Getting the path from the secrets file
print(fetch_credentials("credentials_path"))

# Retrieving a custom credential from the secrets file
print(fetch_credentials("SalesforceSFTP"))
```

## code_location()
Get the location of this script based on the secrets file. It can be "local", "remote" or whatever if fits the description of where the execution of this script takes place.

It's an alias for: fetch_credentials("Location")

Usage example:
```
from instackup.general_tools import code_location

if code_location() == "local":
    # set vars for when the code is executed locally
else:
    # set vars for when the code is executed remotely
```

## unicode_to_ascii(unicode_string)
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

## parse_remote_uri(uri, service)
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
