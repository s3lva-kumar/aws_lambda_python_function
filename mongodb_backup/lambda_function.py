import os
from pymongo import MongoClient
import boto3
from bson.json_util import dumps
from datetime import datetime
import shutil
import json
from dotenv import load_dotenv

load_dotenv()

BUCKET_REGION = os.environ["BUCKET_REGION"]
BUCKET_NAME = os.environ["BUCKET_NAME"]
URI = os.environ["URI"]

def lambda_handler(event, context):
    print("Function started")
    connect = connect_db()
    db_data = json.loads(os.environ["DB_NAME"])
    
    if db_data == ['*'] and len(db_data) == 1:
        take_full_db_backup(connect)
    if db_data != ['*'] and len(db_data) > 0:
        backup(connect, db_data)
    if len(db_data) == 0:
       print("""ERROR: provide the array of collocation names or ["*"]
       ["*"] it means, take the full db backup
             """)
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
      s3 = boto3.client("s3", region_name=BUCKET_REGION) #os.environ("REGION")
      s3.upload_file(local_path, BUCKET_NAME, s3_path)
      print (f'backup pushed to s3: {local_path}')
    except Exception as e:
       print(e)

def connect_db():
    try:
      client = MongoClient(URI)
      return client
    except Exception as e:
       print(e)

def take_full_db_backup(client):
   db_list = client.list_database_names()
   backup(client ,db_list)
   
def backup(client, db_name):
    try:
      today = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
      print(today)
      if not os.path.exists("/tmp/mongodb_backup"):
        os.mkdir("/tmp/mongodb_backup")
      for x in db_name:
        database = client.get_database(x) 
        os.mkdir(f'/tmp/mongodb_backup/{x}')
        for collection_name in database.list_collection_names():
          temp_filepath = f"/tmp/mongodb_backup/{x}/" + collection_name + ".json"
          with open(temp_filepath, "w") as f:
              for doc in database.get_collection(collection_name).find():
                f.write(dumps(doc) + "\n")
        local_path=f"/tmp/mongodb_backup/{x}"
        zipping(local_path)
        push_to_s3(f'{local_path}.zip', f'{x}/{x}-{today}.zip')
      print("Function end")   
    except Exception as e:
       print (f'backup error {e}')