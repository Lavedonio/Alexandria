# gsheets_tools
This is the documentation for the gsheets_tools modules and all its contents, with usage examples.

# Index
- [GSheetsTool](#gsheetstool)
  - [\_\_init\_\_(self, sheet_url=None, sheet_key=None, sheet_gid=None, auth_mode='secret_key', read_only=False, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])](#__init__self-sheet_urlnone-sheet_keynone-sheet_gidnone-auth_modesecret_key-read_onlyfalse-scopeshttpswwwgoogleapiscomauthspreadsheets-httpswwwgoogleapiscomauthdrive)
  - [set_spreadsheet_by_url(self, sheet_url)](#set_spreadsheet_by_urlself-sheet_url)
  - [set_spreadsheet_by_key(self, sheet_key)](#set_spreadsheet_by_keyself-sheet_key)
  - [set_worksheet_by_id(self, sheet_gid)](#set_worksheet_by_idself-sheet_gid)
  - [download(self)](#downloadself)
  - [upload(self, dataframe, write_mode="TRUNCATE")](#uploadself-dataframe-write_modetruncate) _(Not Yet Implemented)_

# Module Contents
## GSheetsTool
This class encapsulates the gspread module to ease the setup process and handle most of the interaction needed with Google Sheets, so the base code becomes more readable and straightforward.

### \_\_init\_\_(self, sheet_url=None, sheet_key=None, sheet_gid=None, auth_mode='secret_key', read_only=False, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
Initialization takes either _sheet_url_ or _sheet_key_ and _sheet_gid_ parameters to first referenciate the worksheet.

_auth_mode_ parameter can either be **secret_key**, which will look for the configured Secret Key, **oauth**, which will prompt a window requiring manual authentication, or **composer**, which will use the current environment to set the credentials to that project.

_read_only_ parameter will convert the scopes to their read only versions. That means that they will can only be seen or downloaded, but not edited.

_scopes_ parameter sets the appropriated scopes to the environment when connecting. Sometimes only the spreadsheets authorization is necessary or can be given.

Usage example:
```
from instackup.gsheets_tools import GSheetsTool


sheet = GSheetsTool(sheet_url="https://docs.google.com/spreadsheets/d/0B7ciWr8lX8LTMVVyajlScU42OU0/edit#gid=214062020")

# or

sheet = GSheetsTool(sheet_key="0B7ciWr8lX8LTMVVyajlScU42OU0", sheet_gid="214062020")
```

### set_spreadsheet_by_url(self, sheet_url)
Set spreadsheet and worksheet attributes by the Spreadsheet URL.

Usage example:
```
from instackup.gsheets_tools import GSheetsTool


sheet = GSheetsTool(sheet_key="0B7ciWr8lX8LTMVVyajlScU42OU0", sheet_gid="214062020")

# Do something with the selected sheet

# Changing Sheets
sheet.set_spreadsheet_by_url("https://docs.google.com/spreadsheets/d/0B7ciWr8lX8LTWjFMQW4yT2MtRlk/edit#gid=324336327")
```

### set_spreadsheet_by_key(self, sheet_key)
Set spreadsheet attribute by the Spreadsheet key value.

Usage example:
```
from instackup.gsheets_tools import GSheetsTool


sheet = GSheetsTool(sheet_key="0B7ciWr8lX8LTMVVyajlScU42OU0", sheet_gid="214062020")

# Do something with the selected sheet

# Changing Sheets (need to setup worksheet before using. See set_worksheet_by_id method)
sheet.set_spreadsheet_by_key("0B7ciWr8lX8LTWjFMQW4yT2MtRlk")
```

### set_worksheet_by_id(self, sheet_gid)
Set worksheet attribute by the Spreadsheet gid value.

Usage example:
```
from instackup.gsheets_tools import GSheetsTool


sheet = GSheetsTool(sheet_key="0B7ciWr8lX8LTMVVyajlScU42OU0", sheet_gid="214062020")

# Do something with the selected sheet

# Changing Sheets
sheet.set_spreadsheet_by_key("0B7ciWr8lX8LTWjFMQW4yT2MtRlk")
sheet.set_worksheet_by_id("324336327")
```

### download(self)
Download the selected worksheet into a Pandas DataFrame. Raises an error if no worksheet is set.

Usage example:
```
from instackup.gsheets_tools import GSheetsTool


sheet = GSheetsTool(sheet_key="0B7ciWr8lX8LTMVVyajlScU42OU0", sheet_gid="214062020")
df = sheet.download()
```

### upload(self, dataframe, write_mode="TRUNCATE")
Not implemented.
