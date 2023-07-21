import os
from pymongo import MongoClient
import boto3
from bson.json_util import dumps
from datetime import datetime
import shutil


db_name = []

def handler(event, context):
    print("Function started")
    data = connect_db()
    backup(data)

# Comprassing
def zipping(root_path):
  try:
    print("compressing", root_path)
    shutil.make_archive(root_path, 'zip', root_dir=root_path)
    shutil.rmtree(root_path)
  except Exception as e:
    print (e)

# # s3 function
def push_to_s3(local_path, s3_path):
    try:
      print("backup pushing...")
      s3 = boto3.client("s3")
      s3.upload_file(local_path, os.environ["BUCKET_NAME"], s3_path)
      print (f'backup pushed to s3: {local_path}')
    except Exception as e:
       print(e)

def connect_db():
    try:
      client = MongoClient(os.environ["URI"])
      return client
    except Exception as e:
       print(e)

def backup(client):
    try:
      today = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
      print(today)
      for x in db_name:
        database = client.get_database(x) 
        os.mkdir(f'/tmp/{x}')
        for collection_name in database.list_collection_names():
          temp_filepath = f"/tmp/{x}/" + collection_name + ".json"
          with open(temp_filepath, "w") as f:
              for doc in database.get_collection(collection_name).find():
                f.write(dumps(doc) + "\n")
        local_path=f"/tmp/{x}"
        zipping(local_path)
        push_to_s3(f'{local_path}.zip', f'{x}/{x}-{today}.zip')
      print("Function end")   
    except Exception as e:
       print (f'backup error {e}')
