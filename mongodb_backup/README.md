## Intro:
  - This Lambda function is designed to facilitate the process of taking MongoDB backups.

  ### _Note:_
  This function specially made for Lambda environment, if you need to configure this function on where else, you should remove the function params "(event, context)".


## ENV setup:
  -  You have to provide the following ENVs in the .env file
       ```
       URI=             # URI of the mongodb 
       BUCKET_NAME=     # your backup storage S3 bucket name
       BUCKET_REGION=   # you backup bucket region
       DB_NAME=         # list of collocation name for take backup ex: ["admin", "local"] (or) you can provide ["*"] to take the all the collocation to backup, if you empty list "[]" it will throw error.
       
       ```
