# wayhome-datamart

This code uses the AWS SAM framework to deploy a serverless application to AWS.

The application collects data from 2 API endpoints from python lambda functions which are both triggered (seperatly) via an eventbridge schedule.

This schedule will run each lambda once per minute.

The data recieved from the API's is stored in a dynamodb table and also written to an s3 bucket. Storing the data in the dynamodb tables is not really necessary for the purposes of this test, but it was to demonstrate multiple data targets.

The data in the s3 bucket is partitioned by year, month and day in order to make it easier for a Glue crawler to parse.

A glue crawler runs on a schedule  and parses/catalogs the date before making it available in a Glue database/table so that it can be consumed by various analytics services such as Athena and Redshift etc.
This is only running for the price index API, but it is simple to do the same for the price data endpoint and then access the 2 tables together for joins etc.

I have created an API endpoint that returns the average price for each city, year and month:

'SELECT year, month, city, avg(price) AS "Average Price" FROM rawindexdata GROUP BY  city, year, month ORDER BY  year, month, city;'

It can be reached here: (it can take a few seconds to run)
https://snti09ycjj.execute-api.eu-west-2.amazonaws.com/Prod/wh-price-data
This is in JSON format but isn't really formatted etc, it was just to demonstrate querying data and making it available.
The query is against the database created by glue and uses Athena to query the data.


This whole project is running in my AWS account and as per the runtime requirement - there is no reason to suspect that it would stop.
While this is obviously just a test, if it were not, the infrastructure created for this test would scale up almost to any level.
More data could easily be added in, parsed by Glue and made available for querying and analytics.

To run the project in a new environment you can either run it against an AWS account or deploy it locally for testing.

Either way, you should install

AWS CLI
and AWS SAM

If running in an AWS account, set up access token etc as per the AWS CLI instructions

Open the wayhome-datamart folder and at the command line run:

- sam build
- followed by sam deploy

to run it locally you will need docker installed but you would then enter

- sam build
- sam local invoke

These instructions are clear: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started-hello-world.html


