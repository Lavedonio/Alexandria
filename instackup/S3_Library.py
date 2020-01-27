import os
import logging
import boto3
from botocore.exceptions import ClientError
from .General_Tools import fetch_credentials


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "S3_Library.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def parse_s3_path(s3_path):
    """Parses a S3 path into bucket and subfolder(s).
    Raises an error if S3 path is with wrong format."""

    # If there isn't at least 3 "/" in the path, it will default to only set bucket name.
    # If there isn't at least 2 "/" in the path, the path has a syntax error.
    try:
        s3_pattern, _, bucket, subfolder = s3_path.split("/", 3)
    except ValueError:
        try:
            s3_pattern, _, bucket = s3_path.split("/", 2)
        except ValueError:
            logger.error(f"Invalid S3 full path '{s3_path}'!")
            raise ValueError(f"Invalid S3 full path '{s3_path}'! Format should be like 's3://<bucket>/<subfolder>/'")
        else:
            subfolder = ""

    # Clean subfolder into something it will not crash a method later
    if len(subfolder) != 0 and not subfolder.endswith("/"):
        subfolder += "/"

    logger.debug(f"s3_pattern: '{s3_pattern}', bucket: '{bucket}', subfolder: '{subfolder}'")

    # Check for valid path
    if s3_pattern != "s3:":
        logger.error(f"Invalid S3 full path '{s3_path}'!")
        raise ValueError(f"Invalid S3 full path '{s3_path}'! Format should be like 's3://<bucket>/<subfolder>/'")

    return bucket, subfolder


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

    def __init__(self, bucket=None, subfolder="", s3_path=None):
        if all(param is not None for param in [bucket, s3_path]):
            logger.error("Specify either bucket name or full s3 path.")
            raise ValueError("Specify either bucket name or full s3 path.")

        # If a s3_path is set, it will find the bucket and subfolder.
        # Even if all parameters are set, it will overwrite the given bucket and subfolder parameters.
        # That means it will have a priority over the other parameters.
        if s3_path is not None:
            bucket, subfolder = parse_s3_path(s3_path)

        # Getting credentials
        aws_creds = fetch_credentials("AWS")

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
        return self.s3.Bucket(self.bucket_name)

    def set_bucket(self, bucket):
        self.bucket_name = bucket

    def set_subfolder(self, subfolder):
        self.subfolder = subfolder

    def set_by_path(self, s3_path):
        self.bucket_name, self.subfolder = parse_s3_path(s3_path)

    def get_s3_path(self):
        return f"s3://{self.bucket_name}/{self.subfolder}"

    def rename_file(self, new_filename, old_filename):
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

        remote_path can take either a full S3 path or a subfolder only one.

        If the remote_path parameter is not set, it will default to whatever subfolder
        is set in instance of the class plus the file name that is being uploaded."""

        if remote_path is None:
            remote_path = self.subfolder + os.path.basename(filename)
        else:
            # Tries to parse as a S3 path. If it fails, ignores this part
            # and doesn't change the value of remote_path parameter
            try:
                bucket, subfolder = parse_s3_path(remote_path)
            except ValueError:
                pass
            else:
                if bucket != self.bucket_name:
                    logger.warning("Path given has different bucket than the one that is currently set. Ignoring bucket from path.")
                    print("WARNING: Path given has different bucket than the one that is currently set. Ignoring bucket from path.")

                # parse_s3_path() function adds a "/" after a subfolder.
                # Since this is a file, the "/" must be removed.
                remote_path = subfolder[:-1]

        logger.debug(f"remote_path: {remote_path}")

        # self.s3.meta.client.upload_file(filename, bucket, remote_path)

        self.bucket.upload_file(filename, remote_path)

    def upload_subfolder(self, folder_path):
        """Uploads a local folder to with prefix as currently set enviroment (bucket and subfolder).
        Keeps folder structure as prefix in S3. Behaves as if it was downloading an entire folder to current path."""

        # Still in development
        raise NotImplementedError

    def download_file(self, remote_path, filename=None):
        """Downloads remote S3 file to local path.

        remote_path can take either a full S3 path or a subfolder only one.

        If the filename parameter is not set, it will default to whatever subfolder
        is set in instance of the class plus the file name that is being downloaded."""

        if filename is None:
            filename = self.subfolder + os.path.basename(remote_path)

        # Tries to parse as a S3 path. If it fails, ignores this part
        # and doesn't change the value of remote_path parameter
        try:
            bucket, subfolder = parse_s3_path(remote_path)
        except ValueError:
            pass
        else:
            if bucket != self.bucket_name:
                logger.warning("Path given has different bucket than the one that is currently set. Ignoring bucket from path.")
                print("WARNING: Path given has different bucket than the one that is currently set. Ignoring bucket from path.")

            # parse_s3_path() function adds a "/" after a subfolder.
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

    def download_subfolder(self):
        """Downloads remote S3 files in currently set enviroment (bucket and subfolder).
        Behaves as if it was downloading an entire folder to current path."""

        # Still in development
        raise NotImplementedError

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
        Raises an error if file doesn't exist and fail_silently parameter is set to False."""

        contents = self.list_contents()

        # Get "folder" object if exists
        if self.subfolder != "":
            if self.subfolder in [x.key for x in self.bucket.objects.filter(Prefix=self.subfolder, Delimiter="/")]:
                contents.append(self.subfolder)
                logger.debug("Subfolder object added to contents list.")

        for file in contents:
            self.s3.Object(self.bucket_name, file).delete()


def test():
    bucket_name = "alexandria-teste"
    s3_path = "s3://revelo-redshift-data/teste_import/"

    s3 = S3Tool(s3_path=s3_path)
    s3_path = "s3://revelo-redshift-data/extraction/"
    s3.set_by_path(s3_path)

    # contents = s3.list_buckets()

    contents = s3.list_contents()

    print("File list now:")
    for index, content in enumerate(contents):
        print(f"{index}: {content}")

    file = "C:\\Users\\USER\\Downloads\\teste.txt"
    new_file = "C:\\Users\\USER\\Downloads\\teste\\teste.txt"
    remote = s3_path + "teste.txt"

    # s3.upload(file)
    # s3.rename_subfolder("extraction_test/")
    # s3.delete_file("teste.txt")
    s3.delete_subfolder()

    contents = s3.list_contents()

    print("\nUpdated file list:")
    for index, content in enumerate(contents):
        print(f"{index}: {content}")

    # s3.download_file(remote)


if __name__ == '__main__':
    test()
