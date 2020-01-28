from instackup.s3_tools import S3Tool


def test():
    bucket_name = "alexandria-teste"
    s3_path = "s3://revelo-redshift-data/teste_import/"

    s3 = S3Tool(s3_path=s3_path)
    s3_path = "s3://revelo-redshift-data/extraction/"
    s3.set_by_path(s3_path)

    # contents = s3.list_buckets()

    contents = s3.list_contents()

    print("File list now:")
    for index, content in enumerate(contents):
        print(f"{index}: {content}")

    file = "C:\\Users\\USER\\Downloads\\teste.txt"
    new_file = "C:\\Users\\USER\\Downloads\\teste\\teste.txt"
    remote = s3_path + "teste.txt"

    # s3.upload(file)
    # s3.rename_subfolder("extraction_test/")
    # s3.delete_file("teste.txt")
    s3.delete_subfolder()

    contents = s3.list_contents()

    print("\nUpdated file list:")
    for index, content in enumerate(contents):
        print(f"{index}: {content}")

    # s3.download_file(remote)


if __name__ == '__main__':
    test()
