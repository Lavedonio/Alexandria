import os
import json
import yaml
import unittest
from instackup.general_tools import fetch_credentials, unicode_to_ascii, parse_remote_uri


class TestFetchCredentials(unittest.TestCase):
    """Unittest for fetch_credentials function in general_tools module of instackup package"""

    def setUp(self):
        self.secrets_filepath = os.environ.get("CREDENTIALS_HOME")

        if self.secrets_filepath is not None:
            _, file_extension = os.path.splitext(self.secrets_filepath)

            # Retrieving secrets from file
            with open(self.secrets_filepath, "r") as stream:
                if file_extension.lower() == ".json":
                    secrets = json.load(stream)
                else:
                    secrets = yaml.safe_load(stream)
        else:
            secrets = None

        self.secrets = secrets

    def tearDown(self):
        if os.environ.get("CREDENTIALS_HOME") is None:
            os.environ["CREDENTIALS_HOME"] = self.secrets_filepath

    def test_environment_variables(self):
        """Test if the environment variables have been set properly"""

        self.assertIsNotNone(os.environ.get("CREDENTIALS_HOME"))

    def test_exception_when_environment_variables_are_not_set(self):
        """Test if raises an exception when there's no environment variable set for 'CREDENTIALS_HOME'"""

        if self.secrets_filepath:
            del os.environ["CREDENTIALS_HOME"]
        self.assertRaises(KeyError, fetch_credentials, "AWS")

    def test_credentials_path(self):
        """Test if the return for the service 'credentials_path' is the directory name of the CREDENTIALS_HOME environment variable"""

        with self.subTest():
            creds_home = os.environ.get("CREDENTIALS_HOME")
            self.assertIsNotNone(creds_home)

        creds_return = fetch_credentials("credentials_path")
        self.assertEqual(creds_return, os.path.dirname(creds_home))

    def test_get_google_credentials(self):
        """Test if Google's credentials file is returned correctly"""

        google_creds = fetch_credentials(service_name="Google")
        self.assertDictEqual(google_creds, self.secrets.get("Google"))

    def test_get_AWS_credentials(self):
        """Test if AWS's credentials are returned correctly"""

        aws_creds = fetch_credentials("AWS")
        self.assertDictEqual(aws_creds, self.secrets.get("AWS"))

    def test_get_redshift_credentials(self):
        """Test if Redshift's database credentials are returned correctly"""

        connection_types = ["cluster_credentials", "master_password"]

        for conn in connection_types:
            with self.subTest(connection_type=conn):

                # Getting info directly from file
                secrets_conn_types = self.secrets.get("RedShift")
                secrets_creds = None
                if secrets_conn_types is not None:
                    secrets_creds = secrets_conn_types.get(conn)

                redshift_creds = fetch_credentials("RedShift", connection_type=conn)
                self.assertDictEqual(redshift_creds, secrets_creds)

    def test_get_bigquery_projectids(self):
        """Test if BigQuery's credentials are returned correctly"""

        # Getting info directly from file
        secrets_dictionary = self.secrets.get("BigQuery")
        secrets_project_ids = None
        if secrets_dictionary is not None:
            secrets_project_ids = secrets_dictionary.get("project_id")

        project_ids = fetch_credentials(service_name="BigQuery", dictionary="project_id")
        self.assertDictEqual(project_ids, secrets_project_ids)


class TestUnicodeToAscii(unittest.TestCase):
    """Unittest for unicode_to_ascii function in general_tools module of instackup package"""

    def test_unicode_to_ascii(self):
        """Test if the function correctly converts every especial character in Portuguese and Spanish to ASCII"""

        utf8_string = "ÁÉÍÓÚÂÊÔÃÕÜÇÑáéíóúâêôãõüçñ"
        ascii_string = "AEIOUAEOAOUCNaeiouaeoaoucn"

        converted_string = unicode_to_ascii(utf8_string)

        self.assertEqual(converted_string, ascii_string)


class TestParseRemoteUri(unittest.TestCase):
    """Unittest for parse_remote_uri function in general_tools module of instackup package"""

    def test_gs_path_only_bucket(self):
        """Test if gs path only containing a bucket name returns expected result"""

        bucket, subfolder = parse_remote_uri("gs://sample_bucket", "gs")
        self.assertTupleEqual((bucket, subfolder), ("sample_bucket", ""))

    def test_gs_path_only_bucket_with_trailing_slash(self):
        """Test if gs path only containing a bucket name and ending with slash returns expected result"""

        bucket, subfolder = parse_remote_uri("gs://sample_bucket/", "gs")
        self.assertTupleEqual((bucket, subfolder), ("sample_bucket", ""))

    def test_gs_path_bucket_and_subfolder(self):
        """Test if gs path containing both bucket and subfolder names returns expected result"""

        bucket, subfolder = parse_remote_uri("gs://sample_bucket/sample_subfolder1/sample_subfolder2", "gs")
        self.assertTupleEqual((bucket, subfolder), ("sample_bucket", "sample_subfolder1/sample_subfolder2/"))

    def test_gs_path_bucket_and_subfolder_with_trailing_slash(self):
        """Test if gs path containing both bucket and subfolder names and ending with slash returns expected result"""

        bucket, subfolder = parse_remote_uri("gs://sample_bucket/sample_subfolder1/sample_subfolder2/", "gs")
        self.assertTupleEqual((bucket, subfolder), ("sample_bucket", "sample_subfolder1/sample_subfolder2/"))

    def test_gs_path_with_wrong_service_name(self):
        """Test if function fails when provided with a path that doesn't match with service name"""

        self.assertRaises(ValueError, parse_remote_uri, "s3://sample_bucket", "gs")

    def test_s3_path_only_bucket(self):
        """Test if s3 path only containing a bucket name returns expected result"""

        bucket, subfolder = parse_remote_uri("s3://sample_bucket", "s3")
        self.assertTupleEqual((bucket, subfolder), ("sample_bucket", ""))

    def test_s3_path_only_bucket_with_trailing_slash(self):
        """Test if s3 path only containing a bucket name and ending with slash returns expected result"""

        bucket, subfolder = parse_remote_uri("s3://sample_bucket/", "s3")
        self.assertTupleEqual((bucket, subfolder), ("sample_bucket", ""))

    def test_s3_path_bucket_and_subfolder(self):
        """Test if s3 path containing both bucket and subfolder names returns expected result"""

        bucket, subfolder = parse_remote_uri("s3://sample_bucket/sample_subfolder1/sample_subfolder2", "s3")
        self.assertTupleEqual((bucket, subfolder), ("sample_bucket", "sample_subfolder1/sample_subfolder2/"))

    def test_s3_path_bucket_and_subfolder_with_trailing_slash(self):
        """Test if s3 path containing both bucket and subfolder names and ending with slash returns expected result"""

        bucket, subfolder = parse_remote_uri("s3://sample_bucket/sample_subfolder1/sample_subfolder2/", "s3")
        self.assertTupleEqual((bucket, subfolder), ("sample_bucket", "sample_subfolder1/sample_subfolder2/"))

    def test_s3_path_with_wrong_service_name(self):
        """Test if function fails when provided with a path that doesn't match with service name"""

        self.assertRaises(ValueError, parse_remote_uri, "gs://sample_bucket", "s3")


if __name__ == '__main__':
    unittest.main()
