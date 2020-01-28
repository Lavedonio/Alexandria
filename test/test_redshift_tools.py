from instackup.redshift_tools import RedShiftTool


def test(using_with_statement=True):

    sql_test_query = """SELECT * FROM atomic.Events LIMIT 10"""

    timestamp = '2019-11-29 19:31:42.766000+00:00'
    extraction_query = """SELECT * FROM atomic.Events WHERE etl_tstamp = '{timestamp}'""".format(timestamp=timestamp)

    s3_path = "s3://revelo-redshift-data/new/"
    filename = "fausto"

    if using_with_statement:
        with RedShiftTool() as snowplow_revelo:
            table = snowplow_revelo.query(sql_test_query, fetch_through_pandas=False)
            print("Query Result by fetchall command:")
            print(table)

            print("")

            df = snowplow_revelo.query(sql_test_query, fail_silently=False)
            print("Query Result by pandas:")
            print(df)

            snowplow_revelo.unload_to_S3(extraction_query, s3_path, filename)

    else:
        snowplow_revelo = RedShiftTool()
        snowplow_revelo.connect()

        table = snowplow_revelo.query(sql_test_query, fetch_through_pandas=False)
        print("Query Result by fetchall command:")
        print(table)

        print("")

        df = snowplow_revelo.query(sql_test_query, fail_silently=False)
        print("Query Result by pandas:")
        print(df)

        snowplow_revelo.unload_to_S3(extraction_query, s3_path, filename)

        snowplow_revelo.close_connection()


if __name__ == '__main__':
    test()
