import os
import json
import logging
import boto3
import pandas as pd


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

file_handler = logging.FileHandler("S3_Library.log")
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

    All that means is that while you may a path as:
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

    def __init__(self, bucket=None, subfolder=None, s3_path=None):
        if all(param is not None for param in [bucket, s3_path]):
            logger.error("Specify either bucket name or full s3 path.")
            raise ValueError("Specify either bucket name or full s3 path.")

        # If a s3_path is set, it will find the bucket and subfolder.
        # Even if all parameters are set, it will overwrite the given bucket and subfolder parameters.
        # That means it will have a priority over the other parameters.
        if s3_path is not None:
            logger.debug(f"s3_path: '{s3_path}'")

            # If there isn't at least 3 "/" in the path, it will default to only set bucket name.
            # If there isn't at least 2 "/" in the path, it has a syntax error.
            try:
                s3_pattern, _, bucket, subfolder = s3_path.split("/", 3)
            except ValueError:
                try:
                    s3_pattern, _, bucket = s3_path.split("/", 2)
                except ValueError:
                    logger.error(f"Invalid S3 full path '{s3_path}'!")
                    raise ValueError(f"Invalid S3 full path '{s3_path}'! Format should be like 's3://<bucket>/<subfolder>/'")

            logger.debug(f"s3_pattern: '{s3_pattern}', bucket: '{bucket}', subfolder: '{subfolder}'")

            # Check for valid path
            if s3_pattern != "s3:":
                logger.error(f"Invalid S3 full path '{s3_path}'!")
                raise ValueError(f"Invalid S3 full path '{s3_path}'! Format should be like 's3://<bucket>/<subfolder>'")

        logger.debug(f"old subfolder: '{subfolder}'")
        
        # CLean subfolder into something it will not crash a method later
        if subfolder is None:
            subfolder = ""
        else:
            if len(subfolder) != 0:
                if subfolder[-1] != "/":
                    subfolder += "/"

        logger.debug(f"cleaned subfolder: '{subfolder}'")

        self.s3 = boto3.resource("s3")
        self.bucket_name = bucket
        self.subfolder = subfolder

    @property
    def bucket(self):
        return self.s3.Bucket(self.bucket_name)

    def list_all_buckets(self):
        """Returns a list of all Buckets in S3"""

        return [bucket.name for bucket in self.s3.buckets.all()]

    def list_bucket_contents(self, bucket=None, subfolder=None, yield_results=False):
        """Lists all files that correspond with the given bucket and subfolder or what it was set at the initialization.
        It can either return a list or yield a generator.
        Lists can be more familiar to use, but if dealing with large amounts of data,
        yielding the results may be a better option.

        For more information on how to use generators and yield, check this video:
        https://www.youtube.com/watch?v=bD05uGo_sVI"""

        if bucket is not None:
            self.bucket_name = bucket

        if yield_results:
            logger.debug("Yielding the results")

            def list_bucket_contents_as_generator(self, subfolder=None):
                if subfolder is None and self.subfolder == "":
                    logger.debug("No subfolder, yielding all files in bucket")
                    
                    for file in self.bucket.objects.all():
                        yield file.key
                
                else:
                    if subfolder is None:
                        subfolder = self.subfolder

                    logger.debug(f"subfolder '{subfolder}' found, yielding all matching files in bucket")
                    for file in self.bucket.objects.filter(Prefix=subfolder, Delimiter="/"):
                        yield file.key
            return list_bucket_contents_as_generator(self, subfolder=subfolder)

        else:
            logger.debug("Listing the results")

            contents = []

            if subfolder is None and self.subfolder == "":
                logger.debug("No subfolder, listing all files in bucket")

                for file in self.bucket.objects.all():
                    contents.append(file.key)
                return contents
            
            else:
                if subfolder is None:
                    subfolder = self.subfolder

                logger.debug(f"subfolder '{subfolder}' found, listing all matching files in bucket")
                for file in self.bucket.objects.filter(Prefix=subfolder, Delimiter="/"):
                    contents.append(file.key)
                return contents


    # def list_all_bucket_contents(bucket, yield_results=True):
    #     """Get a list of all keys in an S3 bucket.
    #     https://alexwlchan.net/2017/07/listing-s3-keys/"""
    #     if yield_results:
    #         print("Yield")
    #         def list_all_bucket_contents_as_generator(bucket):
    #             """Generate all the keys in an S3 bucket."""
    #             kwargs = {'Bucket': bucket}
                
    #             while True:
    #                 resp = self.client.list_objects_v2(**kwargs)
    #                 for obj in resp['Contents']:
    #                     yield obj['Key']

    #                 try:
    #                     kwargs['ContinuationToken'] = resp['NextContinuationToken']
    #                 except KeyError:
    #                     break

    #         return list_all_bucket_contents_as_generator(bucket)
        
    #     else:
    #         print("Not Yield")
    #         keys = []

    #         kwargs = {'Bucket': bucket}
    #         while True:
    #             resp = self.client.list_objects_v2(**kwargs)
    #             for obj in resp['Contents']:
    #                 keys.append(obj['Key'])

    #             try:
    #                 kwargs['ContinuationToken'] = resp['NextContinuationToken']
    #             except KeyError:
    #                 break

    #         return keys


def test():
    bucket_name = "revelo-redshift-data"
    s3_path = "s3://snowplow-emretl-revelo/"

    s3 = S3Tool(bucket=bucket_name)

    contents = s3.list_buckets()

    # contents = s3.list_bucket_contents()

    print(contents)


if __name__ == '__main__':
    test()
