import os
import logging
import pandas as pd
from io import StringIO
from google.cloud import storage
from .general_tools import fetch_credentials, parse_remote_uri


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "gcloudstorage_tools.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class GCloudStorageTool(object):
    """This class handle most of the interaction needed with Google Cloud Storage,
    so the base code becomes more readable and straightforward."""

    def __init__(self, bucket=None, subfolder="", gs_path=None, authenticate=True):
        if all(param is not None for param in [bucket, gs_path]):
            logger.error("Specify either bucket name or full Google Cloud Storage path.")
            raise ValueError("Specify either bucket name or full Google Cloud Storage path.")

        # If a gs_path is set, it will find the bucket and subfolder.
        # Even if all parameters are set, it will overwrite the given bucket and subfolder parameters.
        # That means it will have a priority over the other parameters.
        if gs_path is not None:
            bucket, subfolder = parse_remote_uri(gs_path, "gs")

        if authenticate:
            # Getting credentials
            google_creds = fetch_credentials("Google")
            connect_file = google_creds["secret_filename"]
            credentials_path = fetch_credentials("credentials_path")

            # Sets environment if not yet set
            if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") is None:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(credentials_path, connect_file)

        # Initiating client
        logger.debug("Initiating Google Cloud Storage Client")
        try:
            storage_client = storage.Client()
            logger.info("Connected.")
        except Exception as e:
            logger.exception("Error connecting with Google Cloud Storage!")
            raise e

        self.client = storage_client
        self.bucket_name = bucket
        self.subfolder = subfolder
        self.blob = None

    @property
    def bucket(self):
        self._bucket = self.client.get_bucket(self.bucket_name)
        return self._bucket

    def set_bucket(self, bucket):
        self.bucket_name = bucket

    def set_subfolder(self, subfolder):
        self.subfolder = subfolder

    def set_blob(self, blob):

        # Tries to parse as a gs path. If it fails, ignores this part
        # and doesn't change the value of remote_path parameter
        try:
            bucket, blob = parse_remote_uri(blob, "gs")
        except ValueError:
            pass
        else:
            if bucket != self.bucket_name:
                logger.warning("Path given has different bucket than the one that is currently set. Ignoring bucket from path.")
                print("WARNING: Path given has different bucket than the one that is currently set. Ignoring bucket from path.")

            # parse_remote_uri() function adds a "/" after a subfolder.
            # Since this is a file, the "/" must be removed.
            blob = blob[:-1]

        self.blob = self.bucket.blob(blob)

    def set_by_path(self, gs_path):
        self.bucket_name, self.subfolder = parse_remote_uri(gs_path, "gs")

    def get_gs_path(self):
        if self.blob is None:
            return f"gs://{self.bucket_name}/{self.subfolder}"
        else:
            return f"gs://{self.bucket_name}/{self.blob.name}"

    def list_all_buckets(self):
        """Returns a list of all Buckets in Google Cloud Storage"""

        return [self.get_bucket_info(bucket) for bucket in self.client.list_buckets()]

    def get_bucket_info(self, bucket=None):
        if bucket is None:
            bucket = self.bucket

        return {
            'Name': bucket.name,
            'TimeCreated': bucket._properties.get('timeCreated', ''),
            'TimeUpdated': bucket._properties.get('updated', ''),
            'OwnerID': '' if not bucket.owner else bucket.owner.get('entityId', '')
        }

    def list_bucket_attributes(self):
        """A list of all curently supported bucket attributes that comes in get_bucket_info method return dictionary."""

        return [
            "Name",
            "TimeCreated",
            "TimeUpdated",
            "OwnerID"
        ]

    def get_blob_info(self, blob=None, param=None):
        """Converts a google.cloud.storage.Blob (which represents a storage object) to context format (GCS.BucketObject)."""
        if blob is None:
            blob = self.blob

        blob_info = {
            'Name': blob.name,
            'Bucket': blob.bucket.name,
            'ContentType': blob.content_type,
            'TimeCreated': blob.time_created,
            'TimeUpdated': blob.updated,
            'TimeDeleted': blob.time_deleted,
            'Size': blob.size,
            'MD5': blob.md5_hash,
            'OwnerID': '' if not blob.owner else blob.owner.get('entityId', ''),
            'CRC32c': blob.crc32c,
            'EncryptionAlgorithm': blob._properties.get('customerEncryption', {}).get('encryptionAlgorithm', ''),
            'EncryptionKeySHA256': blob._properties.get('customerEncryption', {}).get('keySha256', ''),
        }

        if param is not None:
            return blob_info[param]
        return blob_info

    def list_blob_attributes(self):
        """A list of all curently supported bucket attributes that comes in get_blob_info method return dictionary."""

        return [
            'Name',
            'Bucket',
            'ContentType',
            'TimeCreated',
            'TimeUpdated',
            'TimeDeleted',
            'Size',
            'MD5',
            'OwnerID',
            'CRC32c',
            'EncryptionAlgorithm',
            'EncryptionKeySHA256'
        ]

    def list_contents(self, yield_results=False):
        """Lists all files that correspond with bucket and subfolder set at the initialization.
        It can either return a list or yield a generator.
        Lists can be more familiar to use, but when dealing with large amounts of data,
        yielding the results may be a better option in terms of efficiency.

        For more information on how to use generators and yield, check this video:
        https://www.youtube.com/watch?v=bD05uGo_sVI"""

        if yield_results:
            logger.debug("Yielding the results")

            def list_contents_as_generator(self):
                if self.subfolder == "":
                    logger.debug("No subfolder, yielding all files in bucket")

                    for blob in self.client.list_blobs(self.bucket_name):
                        yield self.get_blob_info(blob)

                else:
                    logger.debug(f"subfolder '{self.subfolder}' found, yielding all matching files in bucket")

                    for blob in self.client.list_blobs(self.bucket_name, prefix=self.subfolder):
                        blob_dict = self.get_blob_info(blob)
                        if blob_dict["Name"] != self.subfolder:
                            yield blob_dict

            return list_contents_as_generator(self)

        else:
            logger.debug("Listing the results")

            contents = []

            if self.subfolder == "":
                logger.debug("No subfolder, listing all files in bucket")

                for blob in self.client.list_blobs(self.bucket_name):
                    contents.append(self.get_blob_info(blob))

            else:
                logger.debug(f"subfolder '{self.subfolder}' found, listing all matching files in bucket")

                for blob in self.client.list_blobs(self.bucket_name, prefix=self.subfolder):
                    blob_dict = self.get_blob_info(blob)
                    if blob_dict["Name"] != self.subfolder:
                        contents.append(blob_dict)

            return contents

    def rename_file(self, new_filename, old_filename):
        """Rename only filename from path key, so the final result is similar to rename a file."""

        # Still in development
        raise NotImplementedError

    def rename_subfolder(self, new_subfolder):
        """Renames all keys, so the final result is similar to rename a subfolder."""

        # Still in development
        raise NotImplementedError

    def upload_file(self, filename, remote_path=None):
        """Uploads file to remote path in Google Cloud Storage (GS).

        remote_path can take either a full GS path or a subfolder only one.

        If the remote_path parameter is not set, it will default to whatever subfolder
        is set in instance of the class plus the file name that is being uploaded."""

        if remote_path is None:
            remote_path = self.subfolder + os.path.basename(filename)
        else:
            # Tries to parse as a S3 path. If it fails, ignores this part
            # and doesn't change the value of remote_path parameter
            try:
                bucket, subfolder = parse_remote_uri(remote_path, "gs")
            except ValueError:
                pass
            else:
                if bucket != self.bucket_name:
                    logger.warning("Path given has different bucket than the one that is currently set. Ignoring bucket from path.")
                    print("WARNING: Path given has different bucket than the one that is currently set. Ignoring bucket from path.")

                # parse_remote_uri() function adds a "/" after a subfolder.
                # Since this is a file, the "/" must be removed.
                remote_path = subfolder[:-1]

        blob = self.bucket.blob(remote_path)
        print('Uploading file {} to gs://{}/{}'.format(filename, self.bucket_name, remote_path))

        blob.upload_from_filename(filename)

    def upload_subfolder(self, folder_path):
        """Uploads a local folder to with prefix as currently set enviroment (bucket and subfolder).
        Keeps folder structure as prefix in Google Cloud Storage.
        Behaves as if it was downloading an entire folder to current path."""

        # Still in development
        raise NotImplementedError

    def upload_from_dataframe(self, dataframe, file_format='CSV', filename=None, overwrite=False, **kwargs):
        """Uploads a dataframe directly to a file in the file_format given without having to save the file.
        If no filename is given, it uses the one set in the blob and will fail if overwrite is set to False.

        File formats supported are:
        - CSV
        - JSON

        **kwargs are passed directly to .to_csv or .to_json methods (according with the file format chosen).
        The complete documentation of these methods can be found here:
        - CSV: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_csv.html
        - JSON: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_json.html
        """

        # In-memory file so it doesn't need to save a local temporary file
        f = StringIO()

        # Saves dataframe to in-memory file object.
        if file_format.upper() == 'CSV':
            dataframe.to_csv(f, **kwargs)

        elif file_format.upper() == 'JSON':
            dataframe.to_json(f, **kwargs)

        else:
            raise ValueError(f"File format {file_format} not supported. Supported format are 'CSV' and 'JSON'.")

        # Sets the pointer to the start of the in-memory file object
        f.seek(0)

        # Defines blob object and upload location
        if filename is None:
            blob = self.blob
        else:
            blob = self.bucket.blob(f"{self.subfolder}/{filename}")

        # If file exists and can't overwrite, raises an error
        if not overwrite and blob.exists():
            raise FileExistsError("File already exists and overwrite is set to False.")

        # If everything is right, it'll finally upload the file.
        blob.upload_from_file(f)

    def download_file(self, fullfilename=None, replace=False):
        """Downloads remote gs file to local path.

        If the fullfilename parameter is not set, it will default to the currently set blob.

        If replace is set to True and there is already a file downloaded with the same filename and path,
        it will replace the file. Otherwise it will create a new file with a number attached to the end."""

        if self.blob is None:
            raise ValueError("No file selected. Set it with set_blob method first.")

        if fullfilename is None:
            fullfilename = self.get_blob_info(param="Name")

        logger.debug(f"fullfilename: {fullfilename}")

        path, filename = os.path.split(fullfilename)
        logger.debug(f"Path: {path}")
        logger.debug(f"Filename: {filename}")

        # If this filename exists in this directory (yes, the one where this code lays), aborts the download
        if filename in next(os.walk(os.getcwd()))[2] and not replace:
            logger.error("File already exists at {}. Clean the folder to continue.".format(os.path.join(os.getcwd(), filename)))
            raise FileExistsError("File already exists at {}. Clean the folder to continue.".format(os.path.join(os.getcwd(), filename)))

        # Downloads the file
        self.blob.download_to_filename(filename)

        logger.info("Download to temporary location finished successfully")

        # Move the downloaded file to specified directory
        os.makedirs(path, exist_ok=True)
        if os.path.exists(fullfilename) and not replace:
            temp_path, ext = os.path.splitext(fullfilename)
            i = 1
            while os.path.exists(f"{temp_path}_copy_{i}{ext}"):
                i += 1
            fullfilename = f"{temp_path}_copy_{i}{ext}"
            logger.info(f"File renamed to {fullfilename}")
        os.replace(filename, fullfilename)

        logger.info("File moved successfully")
        print("Download finished successfully")

    def download_subfolder(self):
        """Downloads remote Storage files in currently set enviroment (bucket and subfolder).
        Behaves as if it was downloading an entire folder to current path."""

        # Still in development
        raise NotImplementedError

    def download_on_dataframe(self, **kwargs):
        """Use blob information to download file and use it directly on a Pandas DataFrame
        without having to save the file.

        **kwargs are passed directly to pandas.read_csv method.
        The complete documentation of this method can be found here:
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
        """

        if self.blob is None:
            raise ValueError("No file selected. Set it with set_blob method first.")

        logger.debug(f"gs path: {self.get_gs_path()}")
        return pd.read_csv(self.get_gs_path(), **kwargs)

    def delete_file(self):
        """Deletes file in Google Cloud Storage."""

        # Still in development
        raise NotImplementedError

    def delete_subfolder(self):
        """Deletes all files with subfolder prefix, so the final result is similar to deleting a subfolder."""

        # Still in development
        raise NotImplementedError
