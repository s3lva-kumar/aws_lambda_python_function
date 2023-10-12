#!/bin/bash python3
import boto3
from dotenv import load_dotenv
import os

def lambda_handler(event, context): 
    load_dotenv()
    client = boto3.client('lambda', region_name=os.getenv("REGION"))
    response = client.list_functions(FunctionVersion='ALL')
    version_count=[]
    i=1
    for x in response["Functions"]:
        function_name=x["FunctionName"]
        version = client.list_versions_by_function(FunctionName=function_name, MaxItems=100)
        for y in version["Versions"]:
            version_count.append(y["Version"])
        print(f'{function_name}:count:{len(version_count)}:{version_count}')
        while (len(version_count) > 10):
            if (len(version_count) == 10):
                print(f'{function}\'s version count first {len(version_count)}')
                version_count.clear()
                break
            print(f'delete_version:-{function_name}:{version_count[i]}')
            client.delete_function(FunctionName=function_name,Qualifier=version_count[i])
            version_count.pop(i)
        else:
            print(f'{function_name}\'s version count is {len(version_count)}')
            version_count.clear()