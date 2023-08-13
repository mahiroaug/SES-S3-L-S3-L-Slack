import boto3
import pyzmail
import urllib.parse
import json
from logging import getLogger, INFO

logger = getLogger(__name__)
logger.setLevel(INFO)


print('Loading function')

s3 = boto3.resource('s3')

def lambda_handler(event, context):
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
        print('From:', email.get_address('from'))
        print('To:', email.get_address('to'))
        print('Subject:', email.get_subject())
        text = email.text_part.get_payload().decode(email.text_part.charset)
        print('Body:', text)

        bucket_source = s3.Bucket(bucket)
        bucket_source.put_object(ACL='private', Body=text,
                                 Key='text' + "/" + messageid + ".txt", ContentType='text/plain')
        return 'end'
    
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}.'.format(key, bucket))
        raise e
