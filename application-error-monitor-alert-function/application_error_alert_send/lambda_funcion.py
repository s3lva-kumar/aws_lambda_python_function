import base64
import requests
import boto3
import gzip
import json
import logging
import os
import datetime
dynamodb = boto3.resource('dynamodb', region_name="us-east-2")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
client = boto3.client('events')


table=dynamodb.Table('application_critical_issue')
column=[{'columnname': 'alert', 'value': 'yes'}, {'columnname': 'updatetime', 'value': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}]

def logpayload(event):
    logger.setLevel(logging.DEBUG)
    logger.debug(event['awslogs']['data'])
    compressed_payload = base64.b64decode(event['awslogs']['data'])
    uncompressed_payload = gzip.decompress(compressed_payload)
    log_payload = json.loads(uncompressed_payload)
    return log_payload


def error_details(payload):
    error_msg = ""
    log_events = payload['logEvents']
    print(f'logevent: {log_events}')
    logger.debug(payload)
    loggroup = payload['logGroup']
    logstream = payload['logStream']
    lambda_func_name = loggroup.split('/')
    logger.debug(f'LogGroup: {loggroup}')
    logger.debug(f'Logstream: {logstream}')
    logger.debug(f'Function name: {lambda_func_name[2]}')
    logger.debug(log_events)
    for log_event in log_events:
        error_msg += log_event['message']
    logger.debug('Message: %s' % error_msg.split("\n"))
    return loggroup, logstream, error_msg, lambda_func_name

def publish_message(loggroup, logstream, error_msg, lambda_func_name):
    item = table.get_item(
    Key={
        'application': loggroup
    },
    )
    if ("Item" in item and len(item["Item"])>0 and item["Item"]["application"]==str(loggroup) and item["Item"]["alert"]=="yes"):
        for x in column:
            table.update_item(
            Key={'application': loggroup},
            UpdateExpression='SET ' + x["columnname"] + ' = :s',
            ExpressionAttributeValues={':s': x["value"]},
            ReturnValues="UPDATED_NEW"
            )
        print("alert already sent for this loggroup:"+ str(loggroup))
    else:
        for x in column:
            table.update_item(
            Key={'application': loggroup},
            UpdateExpression='SET ' + x["columnname"] + ' = :s',
            ExpressionAttributeValues={':s': x["value"]},
            ReturnValues="UPDATED_NEW"
            )
        sns_arn = os.environ['snsARN']  # Getting the SNS Topic ARN passed in by the environment variables.
        snsclient = boto3.client('sns')
        
        message = ""
        message += "\nLog error  summary" + "\n\n"
        message += "##########################################################\n"
        message += "# Application Name:- " + str(lambda_func_name[2]) + "\n"
        message += "# LogGroup Name:- " + str(loggroup) + "\n"
        message += "# LogStream:- " + str(logstream) + "\n"
        message += "# Log Message:- " + "\n"
        message += "# \t\t" + str(error_msg.split("\n")) + "\n"
        message += "##########################################################\n"
        
        sub = f'Critical error occurred for application -> {lambda_func_name[2]}'
          # Sending the notification...
        snsclient.publish(
            TargetArn=sns_arn,
            Subject=sub,
            Message=message
        )
        client.enable_rule(
            Name='recovered-alert-function',
            EventBusName='default'
        )
def lambda_handler(event, context):
    pload = logpayload(event)
    lgroup, lstream, errmessage, lambdaname = error_details(pload)
    publish_message(lgroup, lstream, errmessage, lambdaname)

