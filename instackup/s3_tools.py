import os
import logging
import boto3
from botocore.exceptions import ClientError
from .general_tools import fetch_credentials, parse_remote_uri


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "s3_tools.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class S3Tool(object):
    """This class handle most of the interaction needed with S3,
    so the base code becomes more readable and straightforward.

    To understand the S3 structure, you need to know it is not a hierarchical filesystem,
    it is only a key-value store, though the key is often used like a file path for organising data,
    prefix + filename.
    More information about this can be read in this StackOverFlow thread:
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
    easier to write and the code easier to read."""

    def __init__(self, uri=None, bucket=None, subfolder="", connection="default"):
        if all(param is not None for param in [bucket, uri]):
            logger.error("Specify either bucket name or an URI.")
            raise ValueError("Specify either bucket name or an URI.")

        # If a uri is set, it will find the bucket and subfolder.
        # Even if all parameters are set, it will overwrite the given bucket and subfolder parameters.
        # That means it will have a priority over the other parameters.
        if uri is not None:
            bucket, subfolder = parse_remote_uri(uri, "s3")

        # Getting credentials
        aws_creds = fetch_credentials("AWS", connection)

        try:
            s3_resource = boto3.resource("s3")
        except ClientError:
            s3_resource = None
            logger.warning("Credentials not set in AWS CLI. Recommended to do so.")
            print("Credentials not set in AWS CLI. Recommended to do so.")

        if s3_resource is None:
            try:
                session = boto3.Session(
                    aws_access_key_id=aws_creds["access_key"],
                    aws_secret_access_key=aws_creds["secret_key"],
                )
                s3_resource = session.resource("s3")
            except Exception as e:
                s3_resource = None
                logger.exception("Invalid AWS credentials")
                print("Invalid AWS credentials")
                raise e

        logger.debug("Connected to S3 by boto3")

        self.s3 = s3_resource
        self.bucket_name = bucket
        self.subfolder = subfolder

    @property
    def bucket(self):
        self._bucket = self.s3.Bucket(self.bucket_name)
        return self._bucket

    @bucket.setter
    def bucket(self, bucket_name):
        self.bucket_name = bucket_name
        self.subfolder = ""  # Resets subfolder
        self._bucket = self.s3.Bucket(self.bucket_name)

    @property
    def uri(self):
        self._uri = f"s3://{self.bucket_name}/{self.subfolder}"
        return self._uri

    @uri.setter
    def uri(self, uri):
        self.bucket_name, self.subfolder = parse_remote_uri(uri, "s3")
        self._uri = uri

    def set_bucket(self, bucket):
        self.bucket_name = bucket
        self.subfolder = ""  # Resets subfolder

    def set_subfolder(self, subfolder):
        # Clean subfolder into something it will not crash a method later
        if len(subfolder) != 0 and not subfolder.endswith("/"):
            subfolder += "/"

        self.subfolder = subfolder

    def rename_file(self, old_filename, new_filename):
        """Rename only filename from path key, so the final result is similar to rename a file."""

        old_key = self.subfolder + old_filename
        new_key = self.subfolder + new_filename

        if old_key not in self.list_contents():
            logger.exception(f"File {old_filename} does not exist in path s3://{self.bucket_name}/{self.subfolder}")
            raise ValueError(f"File {old_filename} does not exist in path s3://{self.bucket_name}/{self.subfolder}")

        source_file = f"{self.bucket_name}/{self.subfolder}{old_filename}"
        self.s3.Object(self.bucket, new_key).copy_from(CopySource=source_file)
        self.s3.Object(self.bucket, old_key).delete()

    def rename_subfolder(self, new_subfolder):
        """Renames all keys, so the final result is similar to rename a subfolder."""

        # Added a / at the end if it was not given with one
        if len(new_subfolder) != 0 and not new_subfolder.endswith("/"):
            new_subfolder += "/"

        contents = self.list_contents()

        # Get "folder" object if exists
        if self.subfolder != "":
            if self.subfolder in [x.key for x in self.bucket.objects.filter(Prefix=self.subfolder, Delimiter="/")]:
                contents.append(self.subfolder)
                logger.debug("Subfolder object added to contents list.")

        for old_key in contents:
            new_key = old_key.replace(self.subfolder, new_subfolder, 1)
            logger.debug(f"old_key: {old_key}")
            logger.debug(f"new_key: {new_key}")

            source_file = f"{self.bucket_name}/{old_key}"
            logger.debug(f"source_file: {source_file}")

            self.s3.Object(self.bucket_name, new_key).copy_from(CopySource=source_file)
            self.s3.Object(self.bucket_name, old_key).delete()

        logger.debug("Setting class subfolder to new_subfolder")
        self.set_subfolder(new_subfolder)

    def list_all_buckets(self):
        """Returns a list of all Buckets in S3"""

        return [bucket.name for bucket in self.s3.buckets.all()]

    def list_contents(self, yield_results=False):
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

                    for file in self.bucket.objects.all():
                        yield file.key

                else:
                    logger.debug(f"subfolder '{self.subfolder}' found, yielding all matching files in bucket")

                    for file in self.bucket.objects.filter(Prefix=self.subfolder, Delimiter="/"):
                        if file.key != self.subfolder:
                            yield file.key

            return list_bucket_contents_as_generator(self)

        else:
            logger.debug("Listing the results")

            contents = []

            if self.subfolder == "":
                logger.debug("No subfolder, listing all files in bucket")

                for file in self.bucket.objects.all():
                    contents.append(file.key)

            else:
                logger.debug(f"subfolder '{self.subfolder}' found, listing all matching files in bucket")

                for file in self.bucket.objects.filter(Prefix=self.subfolder, Delimiter="/"):
                    contents.append(file.key)

                if self.subfolder in contents:
                    contents.remove(self.subfolder)

            return contents

    def upload_file(self, filename, remote_path=None):
        """Uploads file to remote path in S3.

        remote_path can take either a full URI or a subfolder only one.

        If the remote_path parameter is not set, it will default to whatever subfolder
        is set in instance of the class plus the file name that is being uploaded."""

        if remote_path is None:
            remote_path = self.subfolder + os.path.basename(filename)
        else:
            # Tries to parse as an URI. If it fails, ignores this part
            # and doesn't change the value of remote_path parameter
            try:
                bucket, subfolder = parse_remote_uri(remote_path, "s3")
            except ValueError:
                pass
            else:
                if bucket != self.bucket_name:
                    logger.warning("Path given has different bucket than the one that is currently set. Ignoring bucket from path.")
                    print("WARNING: Path given has different bucket than the one that is currently set. Ignoring bucket from path.")

                # parse_remote_uri() function adds a "/" after a subfolder.
                # Since this is a file, the "/" must be removed.
                remote_path = subfolder[:-1]

        logger.debug(f"remote_path: {remote_path}")

        # self.s3.meta.client.upload_file(filename, bucket, remote_path)

        self.bucket.upload_file(filename, remote_path)

    def upload_subfolder(self, folder_path):
        """Uploads a local folder to with prefix as currently set enviroment (bucket and subfolder).
        Keeps folder structure as prefix in S3.
        Behaves as if it was downloading an entire folder to current path."""

        current_path = os.getcwd()
        try:
            os.chdir(folder_path)
            new_root = os.getcwd()

            # Getting only folder name
            folder_path = folder_path.replace("\\", "/")
            folder_path = folder_path + "/" if folder_path[-1] != "/" else folder_path
            upload_folder = folder_path.split[-2]

            print('Uploading local folder {} to s3://{}/{}\n'.format(folder_path, self.bucket_name, self.subfolder + upload_folder))

            for root, dirs, files in os.walk():
                for file in files:
                    local_filename = root + file
                    remote_path = self.subfolder + upload_folder + root.replace(new_root, "").replace("\\", "/") + file

                    print('Uploading file {} to s3://{}/{}'.format(local_filename, self.bucket_name, remote_path))
                    self.bucket.upload_file(local_filename, remote_path)
        except Exception as e:
            raise e
        else:
            print('\nFinished uploading local folder {} to s3://{}/{}'.format(folder_path, self.bucket_name, self.subfolder + upload_folder))
        finally:
            os.chdir(current_path)

    def download_file(self, remote_path, filename=None):
        """Downloads remote S3 file to local path.

        remote_path can take either a full URI or a subfolder only one.

        If the filename parameter is not set, it will default to whatever subfolder
        is set in instance of the class plus the file name that is being downloaded."""

        if filename is None:
            filename = self.subfolder + os.path.basename(remote_path)

        # Tries to parse as an URI. If it fails, ignores this part
        # and doesn't change the value of remote_path parameter
        try:
            bucket, subfolder = parse_remote_uri(remote_path, "s3")
        except ValueError:
            pass
        else:
            if bucket != self.bucket_name:
                logger.warning("Path given has different bucket than the one that is currently set. Ignoring bucket from path.")
                print("WARNING: Path given has different bucket than the one that is currently set. Ignoring bucket from path.")

            # parse_remote_uri() function adds a "/" after a subfolder.
            # Since this is a file, the "/" must be removed.
            remote_path = subfolder[:-1]

        logger.debug(f"remote_path: {remote_path}")

        path, filename = os.path.split(filename)
        logger.debug(f"Path: {path}")
        logger.debug(f"Filename: {filename}")

        # If this filename exists in this directory (yes, the one where this code lays), aborts the download
        if filename in next(os.walk(os.getcwd()))[2]:
            logger.error("File already exists at {}. Clean the folder to continue.".format(os.path.join(os.getcwd(), filename)))
            raise FileExistsError("File already exists at {}. Clean the folder to continue.".format(os.path.join(os.getcwd(), filename)))

        # Downloads the file
        self.bucket.download_file(remote_path, filename)

        # Move the downloaded file to specified directory
        os.makedirs(path, exist_ok=True)
        os.replace(filename, os.path.join(path, filename))

    def download_subfolder(self, download_to=None):
        """Downloads remote S3 files in currently set enviroment (bucket and subfolder)
        to current (or defined in download_to parameter) location.

        Behaves as if it was downloading an entire folder to current path.
        """

        if self.subfolder == "":
            from datetime import datetime
            encoded_datetime = str(datetime.now()).replace(" ", "T").replace(":", "h", 1).replace(":", "m").split(".")[0]
            download_dir = self.bucket_name + "_" + encoded_datetime
        else:
            download_dir = self.subfolder.split("/")[-2]

        # Setting to absolute location if provided
        if download_to is not None:
            download_dir = os.path.join(download_to, download_dir)

        files_to_download = self.list_contents()
        os.makedirs(download_dir, exist_ok=True)

        print("Downloading files...")
        for remote_filename in files_to_download:
            # Creating local folder structure
            *folders, filename = remote_filename.replace(self.subfolder, "", 1).split("/")
            local_folder = os.path.join(download_dir, *folders)
            os.makedirs(local_folder, exist_ok=True)

            # Setting download location
            local_filename = os.path.join(local_folder, filename)

            print(f"Downloading remote file s3://{self.bucket_name}/{remote_filename} to {local_filename}")
            self.bucket.download_file(remote_filename, local_filename)

    def delete_file(self, filename, fail_silently=False):
        """Deletes file. Raises an error if file doesn't exist and fail_silently parameter is set to False."""

        key = self.subfolder + filename
        logger.debug(f"key: {key}")

        if key in self.list_contents():
            self.s3.Object(self.bucket, key).delete()

        else:
            if not fail_silently:
                logger.exception(f"File {filename} does not exist in path s3://{self.bucket_name}/{self.subfolder}")
                raise ValueError(f"File {filename} does not exist in path s3://{self.bucket_name}/{self.subfolder}")

    def delete_subfolder(self):
        """Deletes all files with subfolder prefix, so the final result is similar to deleting a subfolder.
        Once the subfolder is deleted, it resets to no extra path (empty subfolder name)."""

        contents = self.list_contents()

        # Get "folder" object if exists
        if self.subfolder != "":
            if self.subfolder in [x.key for x in self.bucket.objects.filter(Prefix=self.subfolder, Delimiter="/")]:
                contents.append(self.subfolder)
                logger.debug("Subfolder object added to contents list.")

        for file in contents:
            self.s3.Object(self.bucket_name, file).delete()

        # Once the subfolder is deleted, it resets to no extra path
        self.subfolder = ""
