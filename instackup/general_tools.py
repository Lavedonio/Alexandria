import os
import json
import yaml
import logging
import unicodedata


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "general_tools.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def fetch_credentials(service_name, **kwargs):
    """Gets the credentials from the secret file set in CREDENTIALS_HOME variable and
    returns its selected service, which is defined by the service_name parameter, in a dictionary.

    If service is "credentials_path", the path for the directory where
    the secret file is located is returned instead.

    Parses only 1 kwargs, not necessarily in order. Others are discarded.
    """

    # Getting credentials' secret file path
    try:
        secrets_path = os.environ["CREDENTIALS_HOME"]
        logger.debug(f"Environment Variable found: {secrets_path}")
    except KeyError:
        logger.exception('Environment Variable "CREDENTIALS_HOME" not found')
        raise KeyError('Environment Variable "CREDENTIALS_HOME" not found')

    # Getting credentials' folder path
    if service_name == "credentials_path":
        return os.path.dirname(secrets_path)

    # If file extension is ".json", tries to read as a JSON. If not, tries to read as a YAML file.
    _, file_extension = os.path.splitext(secrets_path)

    # Retrieving secrets from file
    with open(secrets_path, "r") as stream:
        if file_extension.lower() == ".json":
            secrets = json.load(stream)
        else:
            secrets = yaml.safe_load(stream)

    # Parses only 1 kwarg if it's passed in function call
    if bool(kwargs):
        second_kwarg, *_ = kwargs.values()
        return secrets[service_name][second_kwarg]
    else:
        return secrets[service_name]


def code_location():
    """Get the location of this script based on the secrets file.
    It can be "local", "remote" or whatever if fits the description of
    where the execution of this script takes place.

    It's an alias for: fetch_credentials("Location")
    """
    return fetch_credentials("Location")


def unicode_to_ascii(unicode_string):
    """Replaces all non-ascii chars in string by the closest possible match.

    This solution was inpired by this answer:
    https://stackoverflow.com/a/517974/11981524
    """
    nfkd_form = unicodedata.normalize('NFKD', unicode_string)
    return "".join([char for char in nfkd_form if not unicodedata.combining(char)])


def parse_remote_uri(uri, service):
    """Parses a Google Cloud Storage (GS) or an Amazon S3 path into bucket and subfolder(s).
    Raises an error if path is with wrong format.

    service parameter can be either "gs" or "s3"
    """

    service = service.lower()  # Ensuring standard

    # If there isn't at least 3 "/" in the path, it will default to only set bucket name.
    # If there isn't at least 2 "/" in the path, the path has a syntax error.
    try:
        uri_service, _, bucket, subfolder = uri.split("/", 3)
    except ValueError:
        try:
            uri_service, _, bucket = uri.split("/", 2)
        except ValueError:
            logger.error(f"Invalid service type ({service}) in URI given '{uri}'!")
            raise ValueError(f"Invalid service type ({service}) in URI given '{uri}'! Format should be like '{service}://<bucket>/<subfolder>/'")
        else:
            subfolder = ""

    # Clean subfolder into something it will not crash a method later
    if len(subfolder) != 0 and not subfolder.endswith("/"):
        subfolder += "/"

    logger.debug(f"uri_service: '{uri_service}', bucket: '{bucket}', subfolder: '{subfolder}'")

    # Check for valid path
    if uri_service[:-1] != service:
        logger.error(f"Invalid service type ({service}) in URI given '{uri}'!")
        raise ValueError(f"Invalid service type ({service}) in URI given '{uri}'! Format should be like '{service}://<bucket>/<subfolder>/'")

    return bucket, subfolder
