import os
import yaml
import logging


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "General_Tools.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def fetch_credentials(service_name, **kwargs):
    """Gets the credentials from the folder set in CREDENTIALS_HOME variable
    and returns the credentials of the selected service in a dictionary."""

    # Getting credential files path
    try:
        credentials_path = os.environ["CREDENTIALS_HOME"]
        logger.debug(f"Environment Variable found: {credentials_path}")
    except KeyError as e:
        logger.exception('Environment Variable "CREDENTIALS_HOME" not found')
        print('Environment Variable "CREDENTIALS_HOME" not found')
        raise e

    # Getting credential secret file path
    try:
        secrets_path = os.environ["CREDENTIALS_SECRET"]
        logger.debug(f"Environment Variable found: {secrets_path}")
    except KeyError as e:
        logger.exception('Environment Variable "CREDENTIALS_SECRET" not found')
        print('Environment Variable "CREDENTIALS_SECRET" not found')
        raise e

    # Retrieving secrets from file
    with open(secrets_path, "r") as stream:
        secrets = yaml.safe_load(stream)

    # Variable connection_type is mainly for RedShift, since it has 2 ways of connecting to the database
    if kwargs.get("connection_type") is not None:
        connection_type = kwargs["connection_type"]
        return secrets[service_name][connection_type]
    else:
        return secrets[service_name]


def test():
    print(fetch_credentials(service_name="Google"))

    print(fetch_credentials("AWS"))

    print(fetch_credentials("RedShift", connection_type="cluster_credentials"))


if __name__ == '__main__':
    test()