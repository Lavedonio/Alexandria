import os
import logging
import gspread
import pandas as pd
from .general_tools import fetch_credentials


# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "gsheets_tools.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class GSheetsTool(object):
    """This class encapsulates the gspread module to ease the setup process and handle most of the
    interaction needed with Google Sheets, so the base code becomes more readable and straightforward."""

    def __init__(self, sheet_url=None, sheet_key=None, sheet_gid=None, auth_mode='secret_key', read_only=False,
                 scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']):

        # >> Convert scopes into readonly if needed
        if read_only:
            if 'https://www.googleapis.com/auth/drive' in scopes:
                scopes = ['https://www.googleapis.com/auth/drive.readonly']
            else:
                scopes = []
            scopes.append('https://www.googleapis.com/auth/spreadsheets.readonly')

        # >> Authorizing and initializing client
        if auth_mode.lower() == 'secret_key':
            # Getting credentials
            google_creds = fetch_credentials("Google")
            connect_file = google_creds["secret_filename"]
            credentials_path = fetch_credentials("credentials_path")

            # Connecting
            gspread_client = gspread.service_account(
                filename=os.path.join(credentials_path, connect_file),
                scopes=scopes
            )

        elif auth_mode.lower() == 'oauth':
            # Connecting
            gspread_client = gspread.oauth(scopes=scopes)

        elif auth_mode.lower() == 'composer':
            from oauth2client.contrib import gce
            creds = gce.AppAssertionCredentials(scope=scopes)
            gspread_client = gspread.authorize(creds)

        else:
            raise ValueError("Authentication mode not recognized. Choose between 'secret_key', 'oauth' or 'composer'.")

        # >> Setting Spreadsheet and Worksheet
        if sheet_url is not None:
            split_url = sheet_url.split("#gid=")
            sheet = gspread_client.open_by_url(split_url[0])

            if len(split_url) == 2:
                try:
                    worksheet_index = [x.id for x in sheet.worksheets()].index(int(split_url[1]))
                except ValueError:
                    raise ValueError(f"Worksheet ID (sheet_gid: {split_url[1]}) not found in {sheet.title} (sheet_key: {sheet.id})")
                worksheet = sheet.get_worksheet(worksheet_index)
            else:
                worksheet = None

        elif sheet_key is not None:
            sheet = gspread_client.open_by_key(sheet_key)
            if sheet_gid is not None:
                try:
                    worksheet_index = [x.id for x in sheet.worksheets()].index(int(sheet_gid))
                except ValueError:
                    raise ValueError(f"Worksheet ID (sheet_gid: {sheet_gid}) not found in {sheet.title} (sheet_key: {sheet.id})")
                worksheet = sheet.get_worksheet(worksheet_index)
            else:
                worksheet = None

        else:
            sheet = None
            worksheet = None

        self.gspread_client = gspread_client
        self.spreadsheet = sheet
        self.worksheet = worksheet

    def set_spreadsheet_by_url(self, sheet_url):
        """Set spreadsheet and worksheet attributes by the Spreadsheet URL."""

        split_url = sheet_url.split("#gid=")
        sheet = self.gspread_client.open_by_url(split_url[0])

        if len(split_url) == 2:
            try:
                worksheet_index = [x.id for x in sheet.worksheets()].index(int(split_url[1]))
            except ValueError:
                raise ValueError(f"Worksheet ID (sheet_gid: {split_url[1]}) not found in {self.spreadsheet.title} (sheet_key: {self.spreadsheet.id})")
            worksheet = sheet.get_worksheet(worksheet_index)
        else:
            worksheet = None

        self.spreadsheet = sheet
        self.worksheet = worksheet

    def set_spreadsheet_by_key(self, sheet_key):
        """Set spreadsheet attribute by the Spreadsheet key value."""

        self.spreadsheet = self.gspread_client.open_by_key(sheet_key)

    def set_worksheet_by_id(self, sheet_gid):
        """Set worksheet attribute by the Spreadsheet gid value."""

        try:
            worksheet_index = [x.id for x in self.spreadsheet.worksheets()].index(int(sheet_gid))
        except ValueError:
            raise ValueError(f"Worksheet ID (sheet_gid: {sheet_gid}) not found in {self.spreadsheet.title} (sheet_key: {self.spreadsheet.id})")
        self.worksheet = self.spreadsheet.get_worksheet(worksheet_index)

    def download(self):
        """Download the selected worksheet into a Pandas DataFrame. Raises an error if no worksheet is set."""

        if self.worksheet is None:
            raise ValueError("No worksheet set. Set it first before downloading.")
        return pd.DataFrame(self.worksheet.get_all_records())

    def upload(self, dataframe, write_mode="APPEND", force_upload=False):
        """Upload the Pandas DataFrame to the selected worksheet. Raises an error if no worksheet is set.

        The write_mode parameter determines how the data will be written and can be one of 3 choices:
        - APPEND: will append the data to what's written in the worksheet;
        - EMPTY: writes data only if there's not data in the wroksheet or if there's just the headers;
        - TRUNCATE: removes any current data and uploads what's in the DataFrame.

        If the force_upload parameter is set to True, it won't validade if the combination of what's
        in the worksheet and what's in the DataFrame fits.
        """

        # Checking worksheet validity
        if self.worksheet is None:
            raise ValueError("No worksheet set. Set it first before uploading.")

        # Checking write_mode parameter validity
        if write_mode.upper() not in ["APPEND", "EMPTY", "TRUNCATE"]:
            raise ValueError("The write_mode parameter can only be set as 'APPEND', 'EMPTY' or 'TRUNCATE'.")

        # In this special setting, it simply clears the worksheet and uploads the data.
        if force_upload and write_mode.upper() == "TRUNCATE":
            self.worksheet.clear()
            self.worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
        else:
            worksheet_dataframe = pd.DataFrame(self.worksheet.get_all_records())

            # Checking current data in worksheet to prevent data corruption
            try:
                assert worksheet_dataframe.columns.values.tolist() == dataframe.columns.values.tolist() or worksheet_dataframe.empty
            except AssertionError:
                if force_upload:
                    pass
                else:
                    raise ValueError("New data columns and inplace data columns don't match. Set force_upload parameter to True to override this check.")

            # According with the write mode that is set, will prepare the DataFrame to be uploaded
            if write_mode.upper() == "TRUNCATE":
                dataframe_to_upload = dataframe

            elif write_mode.upper() == "APPEND":
                dataframe_to_upload = pd.concat([worksheet_dataframe, dataframe], ignore_index=True)

            else:
                if worksheet_dataframe.empty:
                    dataframe_to_upload = dataframe
                else:
                    raise ValueError("Worksheet is not empty. Select other mode or verify the Worksheet.")

            # Clear what's there and upload
            self.worksheet.clear()
            self.worksheet.update([dataframe_to_upload.columns.values.tolist()] + dataframe_to_upload.values.tolist())
