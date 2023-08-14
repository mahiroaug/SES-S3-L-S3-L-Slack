import boto3
import pyzmail
import urllib.parse
import json
import os
import time
from bs4 import BeautifulSoup
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
        plain = extract_plain_text(text)
        print("plain :",plain)
        link_list = find_link(text)
        print("link_list :",link_list)
        
        attachments = [
            {
                "color": "#37438f",
                "title": subject,
                "text": plain,
                **({"fields": [
                    {
                        "title": "link " + str(index + 1), 
                        "value": link, 
                        "short": True
                    } for index, link in enumerate(link_list)]
                } if link_list else {}),
                "footer": "send from " + ",".join(from_addr),
                "ts": int(time.time())
            }
        ]
        
        attachments_json = json.dumps(attachments).encode('utf-8')

        # push bucket
        bucket_source = s3.Bucket(bucket)
        bucket_source.put_object(ACL='private',
                                 Body=attachments_json,
                                 Key=key_output + "/" + messageid + ".json",
                                 ContentType='application/json'
                                 )
        return 'end'
    
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}.'.format(key, bucket))
        raise e


def extract_plain_text(html):
    after = html.replace("<br>", "\n")
    print("replaced raw: ",after)
    
    soup = BeautifulSoup(after, 'html.parser')
    
    # タグを取り除いたプレーンテキストを抽出
    plain_text = soup.get_text()
    
    return plain_text

def find_link(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    link_list = []
    
    # リンク
    links = soup.find_all('a')
    for link in links:
        link_list.append(link.get('href'))
    
    return link_list
