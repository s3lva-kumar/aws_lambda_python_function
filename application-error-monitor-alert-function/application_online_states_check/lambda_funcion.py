import requests
import boto3
import os
import json
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

site_data=json.loads(os.environ["URL"])
sns_arn = os.environ['snsARN']  # Getting the SNS Topic ARN passed in by the environment variables.
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE_NAME']
DYNAMODB_TABLE_REGION=os.environ['DYNAMODB_TABLE_REGION']
dynamodb = boto3.resource('dynamodb', region_name=DYNAMODB_TABLE_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)
snsclient = boto3.client('sns')
def lambda_handler(event, context):
   
   for x in site_data: 
         appname = x["name"]
         url = x["url"]
         data = table.get_item(
          Key={
            'AppName': appname
          }
         )
         r = requests.get(url) 
         result = r.status_code 
         if ("Item" in data):
            lastcode = data["Item"]["statuscode"]
            print(f'{url}:{lastcode}')
            if (lastcode == 200):
               if (result == 200):
                  print(f'{appname} healthy')
                  # return {"application": str(appname), "status": result }
               if(result != 200):
                  message = ""
                  message += "\nLog error  summary" + "\n\n"
                  message += "##########################################################\n"
                  message += "# Application name:- " + str(appname) + "\n"
                  message += "# Application Endpoint:- " + str(url) + "\n"
                  message += "# LogStream:- " + str(datetime.now()) + "\n"
                  message += "# Log Message:- " + "Application status is " + str(result) + "." + " So there is some problem on the application take a look quickly" + "\n" 
                  message += "##########################################################\n"
                    
                  sub = f'Critical Error: Application Down ->{str(appname)}'
                   # Sending the notification...
                  snsclient.publish(
                     TargetArn=sns_arn,
                     Subject=sub,
                     Message=message
                  )
                  
                  update = table.update_item(
                  Key={'AppName': appname},
                  UpdateExpression='SET statuscode = :s',
                  ExpressionAttributeValues={':s': result},
                  ReturnValues="UPDATED_NEW"
                  )
                  responce=update["Attributes"]
                  print(responce)
                  print("email sent for the error")
            if (lastcode != 200):
               if (result == 200): 
                  message = ""
                  message += "\nLog error  summary" + "\n\n"
                  message += "##########################################################\n"
                  message += "# Application name:- " + str(appname) + "\n"
                  message += "# Application Endpoint:- " + str(url) + "\n"
                  message += "# LogStream:- " + str(datetime.now()) + "\n"
                  message += "# Log Message:- " + "Application status is " + str(result) + "." + " The application endpoint down issue has been resolved." + "\n"
                  message += "##########################################################\n"
                    
                  sub = f'Recovered: Application is Up ->{str(appname)}'
                   # Sending the notification...
                  snsclient.publish(
                     TargetArn=sns_arn,
                     Subject=sub,
                     Message=message
                  )
                  
                  update = table.update_item(
                  Key={'AppName': appname},
                  UpdateExpression='SET statuscode = :s',
                  ExpressionAttributeValues={':s': result},
                  ReturnValues="UPDATED_NEW"
                  )
                  responce=update["Attributes"]
                  print(responce)
                  print("Email sent for recovered")
               if (result != 200):
                  print(f'{appname} still not healthy')
         if ("Item" not in data):
            if (result == 200):
               update = table.update_item(
               Key={'AppName': appname},
               UpdateExpression='SET statuscode = :s',
               ExpressionAttributeValues={':s': result},
               ReturnValues="UPDATED_NEW"
               )
               
               table.update_item(
               Key={'AppName': appname},
               UpdateExpression='SET endpoint = :s',
               ExpressionAttributeValues={':s': url},
               ReturnValues="UPDATED_NEW"
               )
               
               responce=update["Attributes"]
               print(responce)
            if (result != 200):
               message = ""
               message += "\nLog error  summary" + "\n\n"
               message += "##########################################################\n"
               message += "# Application name:- " + str(appname) + "\n"
               message += "# Application Endpoint:- " + str(url) + "\n"
               message += "# LogStream:- " + str(datetime.now()) + "\n"
               message += "# Log Message:- " + "Application status is " + str(result) + "." + " So there is some problem on the application take a look quickly" + "\n"
               message += "##########################################################\n"
               sub = f'Critical Error: Application Endpoint Down ->{str(appname)}'
               # Sending the notification...
               snsclient.publish(
                  TargetArn=sns_arn,
                  Subject=sub,
                  Message=message
               )
               
               update = table.update_item(
               Key={'AppName': appname},
               UpdateExpression='SET statuscode = :s',
               ExpressionAttributeValues={':s': result},
               ReturnValues="UPDATED_NEW"
               )
               
               table.update_item(
               Key={'AppName': appname},
               UpdateExpression='SET endpoint = :s',
               ExpressionAttributeValues={':s': url},
               ReturnValues="UPDATED_NEW"
               )
               
               responce=update["Attributes"]
               print(responce)
               print("Email sent for the error")
