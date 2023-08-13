import json
import os

import boto3
from botocore.exceptions import ClientError
import urllib.parse

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from logging import getLogger, INFO
logger = getLogger(__name__)
logger.setLevel(INFO)


print('Loading function')
### lambda #############################################
def lambda_handler(event, context):
    
        
    ### initializer ####################################
    slack_client = WebClient(os.environ.get("SLACK_OAUTH_TOKEN"))
    channel = os.environ.get("SLACK_POST_CHANNEL")
    s3 = boto3.client('s3')
    
    ### load s3 ########################################
    print("============ logger.info ============")
    logger.info(json.dumps(event))
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    messageid = key.split("/")[1] # key sample [ses-output/********] 
    
    print("bucket: ", bucket)
    print("key :",key)
    print("messageid :",messageid)

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        print("----------- S3 object ------------")     
        print("content :",content)
    except Exception as e:
        print('Error:', str(e))
        return {
            'statusCode': 500,
            'body': 'Error reading S3 file'
        }

    ### post slack ####################################
    post_slack(slack_client,channel,content)

    return {
        'statusCode': 200,
        'body': content
    }
    
def post_slack(slack_client, channel, text):
    try:
        response = slack_client.chat_postMessage(
            channel=channel,
            text=text,
            as_user=True
        )
        print("slackResponse: ", response)
    except SlackApiError as e:
        print("Error posting message: {}".format(e))