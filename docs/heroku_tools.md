# heroku_tools
This is the documentation for the heroku_tools modules and all its contents, with usage examples.

# Index
- [HerokuTool](#herokutool)
  - [\_\_init\_\_(self, heroku_path="heroku", app=None, remote=None)](#__init__self-heroku_pathheroku-appnone-remotenone)
  - [app_flag(self) @property](#app_flagself-property)
  - [execute(self, cmd)](#executeself-cmd)

# Module Contents
## HerokuTool
This class encapsulates and handle most of the interaction needed with Heroku CLI, so the base code becomes more readable and straightforward.

### \_\_init\_\_(self, heroku_path="heroku", app=None, remote=None)
Initialization takes an optional parameter _heroku_path_ that's either the PATH variable or the actual path to the CLI app location in the system.

It also takes 2 extra optional parameters: _app_ and _remote_ that specify the current app in use. Doesn't need to fill both, just one is ok. If there's only one registered app, these parameter don't need to be filled.

Usage example:
```
from instackup.heroku_tools import HerokuTool

# Doesn't need to fill both app and remote parameters. This is just for an example.
heroku = HerokuTool(heroku_path="path/to/heroku", app="lavedonio", remote="heroku-staging")
```

### app_flag(self) @property
Returns the app flag string that will be used as part of the program in execute method, based on the app or the remote parameters given in \_\_init\_\_.

### execute(self, cmd)
Executes a Heroku command via the CLI and returns the output.

Usage example:
```
from instackup.heroku_tools import HerokuTool

heroku = HerokuTool(remote="heroku-staging")
result = heroku.execute("releases")

print(result)
```
