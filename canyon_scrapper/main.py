import requests
import threading
import json
import sys
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

TIME_RANGE = 60 # time interval in seconds
PRODUCT_URL = "https://www.canyon.com/fr-fr/velos-de-route/velos-de-course/ultimate/cf-sl/ultimate-cf-sl-7/2751.html"

def send_webhook(size: str):
    url = os.environ.get("SLACK_HOOK_URL") 
    title = (f"Ultimate CF SL 7")
    message = (f"There is some stock in {size} : <{PRODUCT_URL}|Order now> !")
    slack_data = {
        "username": "Canyon stock bot",
        "icon_emoji": ":man-biking:",
        "channel" : "#cycling",
        "attachments": [
            {
                "color": "#9733EE",
                "fields": [
                    {
                        "title": title,
                        "value": message,
                        "short": "false",
                    }
                ]
            }
        ]
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

def check_stock():
    # page = requests.get(PRODUCT_URL)
    page = requests.get('https://www.canyon.com/fr-fr/velos-de-route/velos-endurance/endurace/al/endurace-7/2942.html')

    soup = BeautifulSoup(page.content, 'html.parser') # Parsing content using beautifulsoup
    
    size_blocks = soup.select("div.productConfiguration__variantType")
    availabilities_blocks = soup.select("div.productConfiguration__availabilityMessage")

    for i, availability in enumerate(availabilities_blocks):
        size = size_blocks[i].text.strip()
        if  availability.text.__contains__('Livraison'):
            print(f"Dispo en taille {size} !")
            send_webhook(size)
        else:
            print(f"Taille {size}, Non disponible :(")

    threading.Timer(TIME_RANGE, check_stock).start()

check_stock()
