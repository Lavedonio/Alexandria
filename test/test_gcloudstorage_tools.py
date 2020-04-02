from instackup.gcloudstorage_tools import GCloudStorageTool


def test():
    # cloud_storage = GCloudStorageTool()

    gs_path = "gs://revelo-rais/"

    cloud_storage = GCloudStorageTool(gs_path=gs_path)
    print(cloud_storage.get_bucket_info())
    gs_path = "gs://revelo-rais/RAIS_2014/"
    cloud_storage.set_by_path(gs_path)

    cloud_storage.set_blob("gs://revelo-rais/RAIS_2014/AC2014.txt")
    print(cloud_storage.get_blob_info())

    buckets = cloud_storage.list_all_buckets()
    print("\nBucket list:")
    for index, bucket in enumerate(buckets):
        print(f"{index}: {bucket['Name']}")

    contents = cloud_storage.list_contents()

    print("\nFile list:")
    for index, content in enumerate(contents):
        print(f"{index}: {content['Name']}")

    # filename = "C:\\Users\\USER\\Downloads\\RAIS_2014\\AC2014.txt"

    # cloud_storage.download_file(filename)

    print(cloud_storage.download_on_dataframe(sep=";", encoding="latin1", decimal=","))


if __name__ == '__main__':
    test()
