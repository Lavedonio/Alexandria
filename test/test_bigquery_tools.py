from instackup.bigquery_tools import BigQueryTool


def test():
    bq = BigQueryTool()

    sql_test_query = """SELECT MAX(etl_tstamp) FROM `revelo-hebe.source_fausto.atomic_events`"""
    new_sql_query = """
        SELECT name, email, split(email, '@')[OFFSET(1)] AS domain, profile_status, dashboard_status
        FROM source_revelo_internal.users
        WHERE  employer = false
        AND split(email, '@')[OFFSET(1)] = "hotmail.com"
        LIMIT 75600
    """

    sql_query = """
    SELECT
      users.id,
      users.email,
      users.company_id,
      ga_signup.datehour,
      -- ga_signup.dimension4,
      ga_signup.source,
      ga_signup.medium,
      ga_signup.campaign,
      ga_signup.keyword,
      ga_signup.adcontent,
      ga_signup.goal9completions
    FROM
      `revelo-hebe.source_revelo_internal.users` users
      RIGHT JOIN `revelo-hebe.source_ga_signup_company_id.report` ga_signup ON CAST(users.id AS STRING) = ga_signup.dimension4
    WHERE
      users.employer = true"""

    # print("Iniciando query...")
    # df = bq.query(new_sql_query)
    # print(df.shape)
    # print(df)
    # df.to_csv("query_CRM.csv", sep=",", index=False)
    import pandas as pd
    df = pd.read_csv("C:\\Users\\USER\\Downloads\\apollo-phone_calls-export.csv")
    df.columns = df.columns.str.replace(' ', '_')
    df.columns = df.columns.str.replace('.', '')
    df.columns = df.columns.str.replace('(', '_')
    df.columns = df.columns.str.replace(')', '_')
    df.columns = df.columns.str.replace('/', '_')
    df.columns = df.columns.str.replace('-', '')
    df.columns = df.columns.str.replace('ç', 'c')
    df.columns = df.columns.str.replace('ã', 'a')
    df.columns = df.columns.str.replace('ê', 'e')
    df.columns = df.columns.str.replace('#', 'Num_de')
    for name, _ in df.iteritems():
        # print(name)
        try:
            int(name[0])
        except ValueError:
            pass
        else:
            new_name = "_" + name
            df.rename(columns={name: new_name}, inplace=True)

    dataset = "sandbox"
    table = "calls"

    bq.upload(df, dataset, table)

    # transfer_config = "projects/118480078918/transferConfigs/5e35261a-0000-2d5a-bd96-24058872d28c"
    # print("Starting transfer...")
    # state_response = bq.start_transfer(project_path=transfer_config)
    # state_response = bq.start_transfer(project_name="revelo-hebe", transfer_name="atomic_events_test3")
    # print(f"Transfer status: {state_response}")


if __name__ == '__main__':
    test()
