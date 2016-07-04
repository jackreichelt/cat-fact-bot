from time import sleep
from slackclient import SlackClient
import os
from datetime import datetime
from catfacts import *
from random import choice
from pytz import timezone
import atexit
from tinys3 import Connection

NAME = 'cat_facts'

def get_icon_emoji():
  return choice([
    ':smiley_cat:',
    ':smile_cat:',
    ':joy_cat:',
    ':heart_eyes_cat:',
    ':smirk_cat:',
    ':kissing_cat:',
    ':scream_cat:',
    ':crying_cat_face:',
    ':pouting_cat:',
    ':cat:',
    ':cat2:'
  ])

posted = False

cf = CatFacts()
#channels = {} #Mapping from channel_id to user_id

usage = """
Welcome to Cat Facts!
To subscribe to your daily cat fact, tag me and say "subscribe".
To unsubscribe from this service, tag me and say "unsubscribe".
To get a fact right now, tag me and say "fact"!

Anything else and I'll show you this message to help you out!

If you have any facts you want to add, comments, complaints, or bug reports, message Jack Reichelt.
"""

@atexit.register
def save_subs():
  print('Writing subscribers.')
  cf.write_subscribers()
  conn.upload('subscribers.txt', open('subscribers.txt', 'rb'), 'better-cat-facts')
#     sys.exit(0)
#
# signal.signal(signal.SIGTERM, sigterm_handler)

TOKEN = os.environ.get('TOKEN', None) # found at https://api.slack.com/web#authentication
S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY', None)
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY', None)

conn = Connection(S3_ACCESS_KEY, S3_SECRET_KEY, endpoint='s3-ap-southeast-2.amazonaws.com')

saved_subs = conn.get('subscribers.txt', 'better-cat-facts')
print(saved_subs)

f = open('subscribers.txt', 'wb')
f.write(saved_subs.content)
f.close()

sc = SlackClient(TOKEN)
if sc.rtm_connect() == True:
  print('Connected.')

  sc.api_call("im.list")

  while True:
    response = sc.rtm_read()
    for part in response:
      if 'ims' in part:
        channels = part['ims']
      if part['type'] == 'message':
        if '<@U1MKHKV8U>' in part['text']:
          if 'unsubscribe' in part['text'].lower():
            cf.remove_subscriber(part['channel'].strip())
            save_subs()
            sc.api_call("chat.postMessage", channel=part['channel'], text="We're sorry to see you go.", username=NAME, icon_emoji=':crying_cat_face:')
          elif 'subscribe' in part['text'].lower():
            cf.add_subscriber(part['channel'].strip())
            save_subs()
            sc.api_call("chat.postMessage", channel=part['channel'], text="Thanks for subscribing to cat facts! Here's your complimentary first cat fact!", username=NAME, icon_emoji=':smile_cat:')
            sc.api_call("chat.postMessage", channel=part['channel'], text=cf.get_fact(part['channel'].strip()), username=NAME, icon_emoji=':smile_cat:')
          elif 'fact' in part['text'].lower():
            sc.api_call("chat.postMessage", channel=part['channel'], text=cf.get_fact(part['channel'].strip()), username=NAME, icon_emoji=get_icon_emoji())
            save_subs()
          elif 'list' in part['text'].lower() and part['user'] == 'U0PDQ1P2R':
            sc.api_call("chat.postMessage", channel=part['channel'], text=cf.list_subscribers(), username=NAME, icon_emoji=get_icon_emoji())
          else:
            sc.api_call("chat.postMessage", channel=part['channel'], text=usage, username=NAME, icon_emoji=get_icon_emoji())

    if 0 <= datetime.now(timezone('Australia/Sydney')).time().hour < 1 and posted == True: #midnight to 1am
      print('It\'s a new day.')
      posted = False
    if 15 <= datetime.now(timezone('Australia/Sydney')).time().hour < 17 and posted == False: #3pm to 5pm
      print('It\'s cat fact time!')
      posted = True
      for channel in cf.get_subscribers():
        print('Sending a fact to {}.'.format(channel))
        sc.api_call("chat.postMessage", channel=channel, text=cf.get_fact(channel), username=NAME, icon_emoji=get_icon_emoji())
      save_subs()

    sleep(1)
else:
  print('Connection Failed, invalid token?')