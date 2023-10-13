### Description:
This function is primarily utilized to monitor the status of HTTP(S) applications. In other words, when configured with a cron schedule, it will send requests to the application endpoints based on the cron time. If the response code is not 200, the function will log that the endpoint is not operational.

Additionally, this function will manage the state of the application endpoint in AWS DynamoDB. It will also send an email notification when the application's status is not 200. Once the problematic application returns to an online state, it will send recovery emails as well.

### ENVs update:
This function need this all the following ENNs:
   ```
   URL=[{"name": "", "url": ""}]  # give the list of objects ex: [{"name": "test", "url": "http(s)://test.com"}]
   snsARN=                        # SNS Topic ARN name for end the email to the subscribers 
   DYNAMODB_TABLE_NAME=           # DynamoDB table name to log the endpoint with it status code
   DYNAMODB_TABLE_REGION=         # Region of the Dynamodb table placed.
   ```