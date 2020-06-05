import os
import logging
import subprocess


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "heroku_tools.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class HerokuTool(object):
    """This class encapsulates and handle most of the interaction needed with Heroku CLI,
    so the base code becomes more readable and straightforward."""

    def __init__(self, heroku_path="heroku", app=None, remote=None):
        p_test = subprocess.run(heroku_path, shell=True, capture_output=True)

        if p_test.returncode != 0:
            raise EnvironmentError("Heroku CLI not installed or not able to be reached.")

        self.heroku = heroku_path
        self.app = app
        self.remote = remote

    @property
    def app_flag(self):
        if self.app or self.remote:
            if self.app:
                return "--app " + self.app
            return "--remote " + self.remote
        return ""

    def execute(self, cmd):
        """Executes a Heroku command via the CLI and returns the output."""
        command = " ".join([self.heroku, cmd, self.app_flag]).strip()
        return subprocess.run(command, shell=True, capture_output=True)
