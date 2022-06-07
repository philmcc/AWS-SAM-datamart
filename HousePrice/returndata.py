import time
import boto3
import json

query = 'SELECT year, month, city, avg(price) AS "Average Price" FROM rawindexdata GROUP BY  city, year, month ORDER BY  year, month, city;'

DATABASE = 'houseindexdata'
output='s3://wh-house-price-dl-bucket/athenaoutput/'
# number of retries
RETRY_COUNT = 10

def returndata(event, context):

    client = boto3.client('athena')

    # Execution
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': DATABASE
        },
        ResultConfiguration={
            'OutputLocation': output,
        }
    )

    # get query execution id
    query_execution_id = response['QueryExecutionId']
    print(query_execution_id)

    ## Athena does not return data immediatly so we can't just get the data directly bck from the query.
    ## Instead we need to wait untill the query has reported as succeeded and then retrieve the results independantly.
    ## Results are also stored in s3 untill removed.

    # get execution status
    for i in range(1, 1 + RETRY_COUNT):

        # get query execution
        query_status = client.get_query_execution(QueryExecutionId=query_execution_id)
        query_execution_status = query_status['QueryExecution']['Status']['State']

        if query_execution_status == 'SUCCEEDED':
            print("STATUS:" + query_execution_status)
            break

        if query_execution_status == 'FAILED':
            raise Exception("STATUS:" + query_execution_status)

        else:
            print("STATUS:" + query_execution_status)
            time.sleep(i)
    else:
        client.stop_query_execution(QueryExecutionId=query_execution_id)
        raise Exception('TIME OVER')
        # get query execution id

    # get query results
    result = client.get_query_results(QueryExecutionId=query_execution_id)
    print(str(result))
    output_results = json.dumps(result)
    return {
        'statusCode': 200,
        'headers': {},
        'body': output_results

        }


