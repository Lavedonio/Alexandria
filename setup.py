import setuptools

# Documentation at https://packaging.python.org/tutorials/packaging-projects/
#
# To compile the project into wheel (built distribution) and tar.gz (source archive) files, run the command:
# python setup.py sdist bdist_wheel
#
# To upload the distribution packages into Test PyPI, run the command:
# python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# And to install it:
# pip install -i https://test.pypi.org/simple/ instackup
#
# To upload the distribution packages into PyPI, run the command:
# python -m twine upload dist/*
# And to install it:
# pip install instackup

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="instackup",
    version="0.2.3",
    author="Daniel Lavedonio de Lima",
    author_email="daniel.lavedonio@gmail.com",
    description="A package to ease interaction with cloud services, DB connections and commonly used functionalities in data analytics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lavedonio/instackup",
    packages=setuptools.find_packages(),
    install_requires=[
        'PyYAML>=5.1',
        'boto3>=1.14.0',
        'google-cloud-bigquery>=1.26.0',
        'google-cloud-bigquery-datatransfer>=1.1.0',
        'google-cloud-storage>=1.18.0',
        'grpcio==1.32.0',
        'gcsfs==0.7.1',
        'gspread==3.6.0',
        'mysql-connector-python>=8.0.21',
        'pandas>=1.1.0',
        'psycopg2-binary==2.8.6',
    ],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    platforms=['any'],
)
