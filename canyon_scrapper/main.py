import requests
import threading
import json
import sys
import os
import time, datetime

from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

TIME_RANGE = 10 # time interval in seconds
PRODUCT_URL = "https://www.canyon.com/fr-fr/velos-de-route/velos-de-course/ultimate/cf-sl/ultimate-cf-sl-7/2751.html"
PRODUCT_WITH_STOCK = "https://www.canyon.com/fr-fr/velo-electrique/velo-route-electrique/endurace-on/endurace-on-7.0/2486.html"

def send_webhook(size: str):
    url = os.environ.get("SLACK_HOOK_URL") 
    title = (f"Ultimate CF SL 7")
    message = (f"There is some stock in {size} : <{PRODUCT_URL}|Order now> !")
    slack_data = {
        "username": "Canyon stock bot",
        "icon_emoji": ":man-biking:",
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
    print(f"-- {datetime.datetime.now()} --")
    page = requests.get(PRODUCT_URL)
    # page = requests.get(PRODUCT_WITH_STOCK)

    soup = BeautifulSoup(page.content, 'html.parser') # Parsing content using beautifulsoup
    
    size_blocks = soup.select("div.productConfiguration__variantType")
    availabilities_blocks = soup.select("div.productConfiguration__availabilityMessage")

    if len(size_blocks) == 0:
        print(Exception("product page empty"))
    
    for i, availability in enumerate(availabilities_blocks):
        size = size_blocks[i].text.strip()
        if  'Livraison' in availability.text or 'En stock' in availability.text:
            print(f"Dispo en taille {size} !")
            send_webhook(size)
        else:
            print(f"Taille {size}, Non disponible :(")

while True:
    check_stock()
    time.sleep(TIME_RANGE)
