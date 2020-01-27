# Instackup
This Python library is an open source way to standardize and simplify connections with cloud-based tools and databases and commonly used tools in data manipulation and analysis.

## Index

- [Prerequisites](https://github.com/Lavedonio/instackup#prerequisites)
- [Installation](https://github.com/Lavedonio/instackup#installation)
- [Documentation](https://github.com/Lavedonio/instackup#documentation)
	- [bigquery_tools](https://github.com/Lavedonio/instackup#bigquery_tools)
	- [gcloudstorage_tools](https://github.com/Lavedonio/instackup#gcloudstorage_tools)
	- [redshift_tools](https://github.com/Lavedonio/instackup#redshift_tools)
	- [s3_tools](https://github.com/Lavedonio/instackup#s3_tools)

## Prerequisites
1. Have a [Python 3.6 version or superior](https://www.python.org/downloads/) installed;
2. Create a YAML file with credentials information;
3. [Optional but recommended] Configure an Environment Variable that points where the Credentials file is.

### 1. Have a Python 3.6 version or superior installed
Got to this [link](https://www.python.org/downloads/) e download the most current version that is compatible with this package.

### 2. Create a YAML file with credentials information

Use the files [secret_template.yml](https://github.com/Lavedonio/instackup/blob/master/credentials/secret_template.yml) or [secret_blank.yml](https://github.com/Lavedonio/instackup/blob/master/credentials/secret_blank.yml) as a base or copy and paste the code bellow and modify its values to the ones in your credentials/projects:

```
#################################################################
#                                                               #
#        ACCOUNTS CREDENTIALS. DO NOT SHARE THIS FILE.          #
#                                                               #
# Specifications:                                               #
# - For the credentials you don't have, leave it blank.         #
# - Keep Google's secret file in the same folder as this file.  #
# - BigQuery project_ids must be strings, i.e., inside quotes.  #
#                                                               #
# Recommendations:                                              #
# - YAML specification: https://yaml.org/spec/1.2/spec.html     #
# - Keep this file in a static path like a folder within the    #
# Desktop. Ex.: C:\Users\USER\Desktop\Credentials\secret.yml    #
#                                                               #
#################################################################


Google:
  secret_filename: file.json

BigQuery:
  project_id:
    project_name: "000000000000"

AWS:
  access_key: AWSAWSAWSAWSAWSAWSAWS
  secret_key: ÇçasldUYkfsadçSDadskfDSDAsdUYalf

RedShift:
  cluster_credentials:
    dbname: db
    user: masteruser
    host: blablabla.random.us-east-2.redshift.amazonaws.com
    cluster_id: cluster
    port: 5439
  master_password:
    dbname: db
    user: masteruser
    host: blablabla.random.us-east-2.redshift.amazonaws.com
    password: masterpassword
    port: 5439
```
Save this file with `.yml` extension in a folder where you know the path won't be modified, like the Desktop folder (Example: `C:\Users\USER\Desktop\Credentials\secret.yml`).

### 3. [Optional but recommended] Configure an Environment Variable that points where the Credentials file is.

To configure the Environment Variable, follow the instructions bellow, based on your Operating System.

#### Windows
1. Place the YAML file in a folder you won't change its name or path later;
2. In Windows Search, type `Environment Variables` and click in the Control Panel result;
3. Click on the button `Environment Variables...`;
4. In **Environment Variables**, click on the button `New`;
5. In **Variable name** type `CREDENTIALS_HOME` and in **Variable value** paste the full path to the recently created YAML file;
6. Click **Ok** in the 3 open windows.

#### Linux/MacOS
1. Place the YAML file in a folder you won't change its name or path later;
2. Open the file `.bashrc`. If it doesn't exists, create one in the `HOME` directory. If you don't know how to get there, open the Terminal, type `cd` and then **ENTER**;
3. Inside the file, in a new line, type the command: `export CREDENTIALS_HOME="/path/to/file"`, replacing the content inside quotes by the full path to the recently created YAML file;
4. Save the file and restart all open Terminal windows.

> **Note:** If you don't follow this last prerequisite, you need to set the environment variable manually inside the code. To do that, inside your python code, after the imports, type the command (replacing the content inside quotes by the full path to the recently created YAML file):

```
os.environ["CREDENTIALS_HOME"] = "/path/to/file"
```

## Installation
Go to the Terminal and type:

    pip install -i https://test.pypi.org/simple/ instackup

## Documentation
### bigquery_tools
*To be defined...*

### gcloudstorage_tools
*To be defined...*

### redshift_tools
*To be defined...*

### s3_tools
*To be defined...*

