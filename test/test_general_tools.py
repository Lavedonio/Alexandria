from instackup.general_tools import fetch_credentials


def test():
    print(fetch_credentials(service_name="Google"))

    print(fetch_credentials("AWS"))

    print(fetch_credentials("RedShift", connection_type="cluster_credentials"))

    print(fetch_credentials("credentials_path"))


if __name__ == '__main__':
    test()
