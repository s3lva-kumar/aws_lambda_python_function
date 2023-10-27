import os
import boto3
import datetime
dynamodb = boto3.resource('dynamodb', region_name="us-east-2")
table=dynamodb.Table('application_critical_issue')
client = boto3.client('events')

def all_projects():
    projects = table.scan()
    # print(projects)
    return(projects["Items"])
       
def delete_item(items):
    for x in items:
        currentdate=datetime.datetime.strptime(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")
        status=datetime.datetime.strptime(x["updatetime"],"%Y-%m-%d %H:%M:%S")<currentdate-datetime.timedelta(minutes=20)
        if (status == True):
            table.delete_item(
                Key={
                    "application": x["application"]
                }
            )
            sns_arn = os.environ['snsARN']  # Getting the SNS Topic ARN passed in by the environment variables.
            snsclient = boto3.client('sns')
            appname = x["application"].split('/')
            message = ""
            message += "\nLog error  summary" + "\n\n"
            message += "##########################################################\n"
            message += "# LogGroup Name:- " + str(appname[2]) + "\n"
            message += "# LogStream:- " + str(currentdate) + "\n"
            message += "# Log Message:- Recovered: The critical issue has been resolved for this application " + str(appname[2])
            message += "##########################################################\n"
        
            sub = f'Recovered: critical error resolved for application -> {appname[2]}'
            # Sending the notification...
            snsclient.publish(
                TargetArn=sns_arn,
                Subject=sub,
                Message=message
            )
def lambda_handler(event, context):
    tabledate = all_projects()
    if (tabledate == []):
        client.disable_rule(
        Name=os.environ["EVENT_BRIDGE_NAME"],
        EventBusName='default'
        )
        print(f'lambda function off')
    else:
        delete_item(tabledate)
    

