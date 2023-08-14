import json
import os
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from logging import getLogger, INFO
logger = getLogger(__name__)
logger.setLevel(INFO)

load_dotenv()

def main():    
    ### initializer ####################################
    slack_client = WebClient(os.environ.get("SLACK_OAUTH_TOKEN"))
    channel = os.environ.get("SLACK_POST_CHANNEL")
    
    ### make text #####################################
    
    raw = """
    <b>Notice: This email contains notifications for the prater network!</b><br><br>Your validator(s) missed an attestation<br>====<br><br>Validator <a href="https://goerli.beaconcha.in/validator/399556">399556</a> missed an attestation at slot <a href="https://goerli.beaconcha.in/slot/6285589">6285589</a>.<br>

― You are receiving this because you are staking on Ethermine Staking. You can manage your subscriptions at <a href="https://goerli.beaconcha.in/user/notifications" style="color: white" onMouseOver="this.style.color='#F5B498'" onMouseOut="this.style.color='#FFFFFF'">Manage</a>.
    """
    
    plain = extract_plain_text(raw)
    print("plain :",plain)
    link_list = find_link(raw)
    print("link_list :",link_list)
    
    attachments = [
        {
            "color": "#37438f",
            "title": "mail subject",
            "text": plain,
            "fields": [
                {
                    "title": "link " + str(index + 1), 
                    "value": link, 
                    "short": True
                } for index, link in enumerate(link_list)
            ],
            "image_url": "",
            "footer": "send from aaaaaa",
            "ts": int(time.time())
        }
    ]


    ### post slack ####################################
    content=post_slack(slack_client,channel,attachments)

    return {
        'statusCode': 200,
        'body': content
    }


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

def post_slack(slack_client, channel, attachments):
    try:
        response = slack_client.chat_postMessage(
            channel=channel,
            attachments=attachments,
            as_user=True
        )
        print("slackResponse: ", response)
    except SlackApiError as e:
        print("Error posting message: {}".format(e))


if __name__ == "__main__":
    main()