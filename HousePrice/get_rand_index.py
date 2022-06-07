import json
import requests
import boto3
import os
from datetime import date, timedelta
import smart_open

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
RESOURCE = 'rand_price_index_func'

def get_rand_price_index(event, context):
    ## Function to grab data from the random price index API and store the data for processing later

    ## Unpack and store the data in dynamodb
    db = boto3.resource('dynamodb')
    tbl = db.Table(os.environ['INDEX_TABLE_NAME'])

    api_result = requests.get(
        'https://europe-west2-wayhome-data-engineer-test.cloudfunctions.net/random-price-index')
    data = json.dumps(api_result.json())
    rand_price_index_dict = json.loads(data)['results']
    print(rand_price_index_dict)

    ## Loop through the result set and insert each record into its own 'item' in dynamodb
    ## Trying to insert the same records again will gracefilly fail so it is not worth checking for duplicate data ahead of the insert
    ## checking then inserting would use twice the resources in dynamodb of just inserting and letting it fail.
    for record in rand_price_index_dict:
        print(record)
        tbl.put_item(
            Item={
                'city': record['city'],
                'date': record['date'],
                'price': record['price'],
            })
        response = tbl.get_item(Key={
            'date': record['date'],
            'city': record['city']
        })
        #print('RESPONSE = ' + str(response))

    ## Lets also put the data into s3 so that we can clean it with glue and easily create reporting dashboards through quicksite
    ## Storing it in s3 gives us a cheap way to keep a lot of data as well as the flexability to process and interperet that data in as yet undefined ways.
    ## There should be a check here to see if the data already exists (I would probably use a conditionexpression in the above dynamodb insert to check) and only insert if it is a new record.
    ## However as the plan is to use Glue to clean the data, it can also deduplicate any records as part of its proceeing - I would want to do this anyway in case somethin gslipped through.

    for record in rand_price_index_dict:
        ds = date.fromisoformat(record['date'])

        key_opts = {
            'bucket_name': 'wh-house-price-dl-bucket',
            'year': ds.year,
            'month': "{:02d}".format(ds.month),
            'day': "{:02d}".format(ds.day),
            'filename': str(record['city'] + '.json')
        }

        ## Set up the directory structure in a way that will make it easy for the Glue crawlers to catalog (Glue not implemented here yet)
        s3_url = "s3://{bucket_name}/rawindexdata/year={year}/month={month}/day={day}/{filename}".format(
            **key_opts)

        tp = {'session': boto3.Session()}

        ## Store the json object in an S3 bucket according to the date
        try:
            with smart_open.open(s3_url, 'wb', transport_params=tp) as fo:
                fo.write(json.dumps(record).encode('utf-8'))
        except Exception as e:
            logger.error({
                'resource': RESOURCE,
                'operation': 'save price index data to s3',
                'error': str(e)
            })
            raise e



    return{
        'statusCode': 200,
        'headers': {},
        'body': json.dumps({'message': 'Data Stored'})
    }
