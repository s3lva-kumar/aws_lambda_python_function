### Intro

This is a function for deleting the lambda version in AWS. Sometimes, we aren't able to update the lambda function, because the lambda version storage limit is exceeded. That time, we can't able to delete the lambda version one by one. So that time we can use this function.


## Dependence: 
  Run the following command to install the packages
  ```python 
    pip3 install -r requirements.txt
  ```
## ENV:
  We need the "REGION" variable only.

## Policy:
  Configure the Lambda full access policy for this function.

## Note:
  This function specially made for Lambda envrinment, if you need to configure this function on where else, you should remove the function params "(event, context)".


 