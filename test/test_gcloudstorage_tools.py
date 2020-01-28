from instackup.gcloudstorage_tools import GCloudStorageTool


def test():
    cloud_storage = GCloudStorageTool()

    gs_path = "gs://revelo_app_etl/"

    cloud_storage = GCloudStorageTool(gs_path=gs_path)
    gs_path = "gs://revelo_app_etl/revelo-app/"
    cloud_storage.set_by_path(gs_path)

    buckets = cloud_storage.list_all_buckets()
    print("Bucket list:")
    for index, bucket in enumerate(buckets):
        print(f"{index}: {bucket}")

    contents = cloud_storage.list_bucket_contents()

    print("File list:")
    for index, content in enumerate(contents):
        print(f"{index}: {content}")

    # file = "C:\\Users\\USER\\Downloads\\teste.txt"
    # new_file = "teste.txt"
    # remote = "teste/teste.txt"

    # cloud_storage.upload_file(file)

    # contents = cloud_storage.list_bucket_contents()

    # print("\nUpdated file list:")
    # for index, content in enumerate(contents):
    #     print(f"{index}: {content}")

    # cloud_storage.download_file(remote, new_file)


if __name__ == '__main__':
    test()
