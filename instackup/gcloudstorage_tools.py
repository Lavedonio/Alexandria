import os
import logging
from google.cloud import storage
from .general_tools import fetch_credentials


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "gcloudstorage_tools.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def parse_gs_path(gs_path):
    """Parses a Google Cloud Storage (GS) path into bucket and subfolder(s).
    Raises an error if GS path is with wrong format."""

    # If there isn't at least 3 "/" in the path, it will default to only set bucket name.
    # If there isn't at least 2 "/" in the path, the path has a syntax error.
    try:
        gs_pattern, _, bucket, subfolder = gs_path.split("/", 3)
    except ValueError:
        try:
            gs_pattern, _, bucket = gs_path.split("/", 2)
        except ValueError:
            logger.error(f"Invalid S3 full path '{gs_path}'!")
            raise ValueError(f"Invalid S3 full path '{gs_path}'! Format should be like 's3://<bucket>/<subfolder>/'")
        else:
            subfolder = ""

    # Clean subfolder into something it will not crash a method later
    if len(subfolder) != 0 and not subfolder.endswith("/"):
        subfolder += "/"

    logger.debug(f"gs_pattern: '{gs_pattern}', bucket: '{bucket}', subfolder: '{subfolder}'")

    # Check for valid path
    if gs_pattern != "gs:":
        logger.error(f"Invalid Google Cloud Storage full path '{gs_path}'!")
        raise ValueError(f"Invalid Google Cloud Storage full path '{gs_path}'! Format should be like 'gs://<bucket>/<subfolder>/'")

    return bucket, subfolder


class GCloudStorageTool(object):
    """This class handle most of the interaction needed with Google Cloud Storage,
    so the base code becomes more readable and straightforward."""

    def __init__(self, bucket=None, subfolder="", gs_path=None):
        if all(param is not None for param in [bucket, gs_path]):
            logger.error("Specify either bucket name or full Google Cloud Storage path.")
            raise ValueError("Specify either bucket name or full Google Cloud Storage path.")

        # If a gs_path is set, it will find the bucket and subfolder.
        # Even if all parameters are set, it will overwrite the given bucket and subfolder parameters.
        # That means it will have a priority over the other parameters.
        if gs_path is not None:
            bucket, subfolder = parse_gs_path(gs_path)

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

    @property
    def bucket(self):
        self._bucket = self.client.get_bucket(self.bucket_name)
        return self._bucket

    def set_bucket(self, bucket):
        self.bucket_name = bucket

    def set_subfolder(self, subfolder):
        self.subfolder = subfolder

    def set_by_path(self, gs_path):
        self.bucket_name, self.subfolder = parse_gs_path(gs_path)

    def get_gs_path(self):
        return f"gs://{self.bucket_name}/{self.subfolder}"

    def list_all_buckets(self):
        """Returns a list of all Buckets in Google Cloud Storage"""

        return [bucket for bucket in self.client.list_buckets()]

    def list_bucket_contents(self, yield_results=False):
        """Lists all files that correspond with bucket and subfolder set at the initialization.
        It can either return a list or yield a generator.
        Lists can be more familiar to use, but when dealing with large amounts of data,
        yielding the results may be a better option in terms of efficiency.

        For more information on how to use generators and yield, check this video:
        https://www.youtube.com/watch?v=bD05uGo_sVI"""

        if yield_results:
            logger.debug("Yielding the results")

            def list_bucket_contents_as_generator(self):
                if self.subfolder == "":
                    logger.debug("No subfolder, yielding all files in bucket")

                    for blob in self.client.list_blobs(self.bucket_name):
                        yield str(blob)

                else:
                    logger.debug(f"subfolder '{self.subfolder}' found, yielding all matching files in bucket")

                    for blob in self.client.list_blobs(self.bucket_name, prefix=self.subfolder):
                        yield str(blob)

            return list_bucket_contents_as_generator(self)

        else:
            logger.debug("Listing the results")

            contents = []

            if self.subfolder == "":
                logger.debug("No subfolder, listing all files in bucket")

                for blob in self.client.list_blobs(self.bucket_name):
                    contents.append(blob)

            else:
                logger.debug(f"subfolder '{self.subfolder}' found, listing all matching files in bucket")

                for blob in self.client.list_blobs(self.bucket_name, prefix=self.subfolder):
                    contents.append(blob)

            return contents

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
                bucket, subfolder = parse_gs_path(remote_path)
            except ValueError:
                pass
            else:
                if bucket != self.bucket_name:
                    logger.warning("Path given has different bucket than the one that is currently set. Ignoring bucket from path.")
                    print("WARNING: Path given has different bucket than the one that is currently set. Ignoring bucket from path.")

                # parse_gs_path() function adds a "/" after a subfolder.
                # Since this is a file, the "/" must be removed.
                remote_path = subfolder[:-1]

        blob = self.bucket.blob(remote_path)
        print('Uploading file {} to gs://{}/{}'.format(filename, self.bucket_name, remote_path))

        blob.upload_from_filename(filename)

    def download_file(self, remote_path, filename=None):
        # Method still in development
        raise NotImplementedError
