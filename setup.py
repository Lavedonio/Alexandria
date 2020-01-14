import setuptools

# Documentation at https://packaging.python.org/tutorials/packaging-projects/
#
# To compile the project into wheel (built distribution) and tar.gz (source archive) files, run the command:
# python setup.py sdist bdist_wheel
#
# To upload the distribution packages into Test PyPI, run the command:
# python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# And to install it:
# pip install -i https://test.pypi.org/simple/ alexandria-lavedonio
#
# To upload the distribution packages into PyPI, run the command:
# python -m twine upload dist/*
# And to install it:
# pip install alexandria-lavedonio

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="alexandria-lavedonio",
    version="0.0.7",
    author="Daniel Lavedonio de Lima",
    author_email="daniel.lavedonio@gmail.com",
    description="A package to help with DB connections and commonly used functionally in data analytics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lavedonio/alexandria",
    packages=setuptools.find_packages(),
    install_requires=[
        'pyyaml',
        'boto3',
        'google-cloud-bigquery',
        'google-cloud-bigquery-datatransfer',
        'google-cloud-storage',
        'pandas',
        'psycopg2',
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
