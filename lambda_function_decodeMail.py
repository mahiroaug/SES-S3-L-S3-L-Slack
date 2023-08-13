import boto3
import pyzmail
import urllib.parse
import json
import os
import time
from logging import getLogger, INFO

logger = getLogger(__name__)
logger.setLevel(INFO)

s3 = boto3.resource('s3')

print('Loading function')
### lambda #############################################
def lambda_handler(event, context):
            
    ### initializer ####################################
    key_output = os.environ.get("KEY_TEXT_OUTPUT")
    
    print("============ logger.info ============")
    logger.info(json.dumps(event))
    
    # Get the object
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    messageid = key.split("/")[1] # key sample [ses-output/********] 
    
    print("bucket: ", bucket)
    print("key :",key)
    print("messageid :",messageid)
    
    try:
        response = s3.meta.client.get_object(Bucket=bucket, Key=key)
        email_body = response['Body'].read()
        email_message = pyzmail.PyzMessage.factory(email_body)
        print("email_message :",email_message)

        print("============ parse ============")
        # Extract information from the email
        email = email_message
        from_addr = email.get_address('from')
        to_addr = email.get_address('to')
        subject = email.get_subject()
        text = email.text_part.get_payload().decode(email.text_part.charset)
        
        print('From:', from_addr)
        print('To:', to_addr)
        print('Subject:', subject)
        print('Body:', text)

        # create put_message
        put_message = f"*{subject}* _FROM {from_addr}_\n```{text}```"
        
        # create put_message2
        put_message2 = {
            "attachments": [
                {
                    "fallback": "Plain-text summary of the attachment.",
                    "color": "#ffc0cb",
                    "pretext": "Email receiving",
                    "title": subject,
                    "title_link": "https://api.slack.com/",
                    "text": text,
                    "footer": "from " + from_addr,
                    "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                    "ts": int(time.time())
                }
            ]
        }

        # push bucket
        bucket_source = s3.Bucket(bucket)
        bucket_source.put_object(ACL='private',
                                 Body=put_message,
                                 Key=key_output + "/" + messageid + ".txt",
                                 ContentType='text/plain'
                                 )
        return 'end'
    
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}.'.format(key, bucket))
        raise e
