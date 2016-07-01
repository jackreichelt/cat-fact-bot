from time import sleep
from slackclient import SlackClient
import os
from datetime import datetime
from catfacts import *
from random import choice
from pytz import timezone

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
channels = {} #Mapping from channel_id to user_id

usage = """
Welcome to Cat Facts!
To subscribe to your daily cat fact, tag me and say "subscribe".
To unsubscribe from this service, tag me and say "unsubscribe".
To get a fact right now, tag me and say "fact"!

Anything else and I'll show you this message to help you out!

If you have any facts you want to add, comments, complaints, or bug reports, message Jack Reichelt.
"""

token = os.environ.get('TOKEN', None) # found at https://api.slack.com/web#authentication
sc = SlackClient(token)
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
            cf.remove_subscriber(part['user'])
            channels.pop(part['channel'])
            sc.api_call("chat.postMessage", channel=part['channel'], text="We're sorry to see you go.", username=NAME, icon_emoji=':crying_cat_face:')
          elif 'subscribe' in part['text'].lower():
            cf.add_subscriber(part['user'])
            channels[part['channel']] = part['user']
            sc.api_call("chat.postMessage", channel=part['channel'], text="Thanks for subscribing to cat facts!", username=NAME, icon_emoji=':smile_cat:')
          elif 'fact' in part['text'].lower():
            sc.api_call("chat.postMessage", channel=part['channel'], text=cf.get_fact(part['user']), username=NAME, icon_emoji=get_icon_emoji())
          else:
            sc.api_call("chat.postMessage", channel=part['channel'], text=usage, username=NAME, icon_emoji=get_icon_emoji())

    if 0 < datetime.now(timezone('Australia/Sydney')).time().hour < 1: #midnight to 1am
      print('It\'s a new day.')
      posted = False
    if 15 < datetime.now(timezone('Australia/Sydney')).time().hour < 16 and posted == False: #3pm to 4pm
      print('It\'s cat fact time!')
      posted = True
      for channel, user in channels.iteritems():
        sc.api_call("chat.postMessage", channel=channel, text=cf.get_fact(user), username=NAME, icon_emoji=get_icon_emoji())

    sleep(1)
else:
  print('Connection Failed, invalid token?')