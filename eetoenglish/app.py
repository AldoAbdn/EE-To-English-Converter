#!/usr/bin/env python
"""Python app for reading evening express tweets

This is a bot that replies to the evening express twitter page with the contents of their articles. 
This is because they often hide the content of their site behind adds. 
"""
#Imports
from dotenv import load_dotenv 
load_dotenv()
import os
from flask import Flask
import tweepy
from eetoenglish.stream_listener.StreamListener import StreamListener
from urllib3.exceptions import ProtocolError

#Setup Auth
auth = tweepy.OAuthHandler(os.environ["CONSUMER_TOKEN"], os.environ["CONSUMER_SECRET"])
auth.set_access_token(os.environ["KEY"], os.environ["SECRET"])

#API
api = tweepy.API(auth)


#Create Stream Listener
streamlistener = StreamListener(api, appendage=os.environ["APPENDAGE"], hashtags=os.environ["HASHTAGS"], tweet_size=int(os.environ["TWEET_SIZE"]))
stream = tweepy.Stream(auth=api.auth, listener=streamlistener)
stream.filter(follow=['19765204',],track=['#EEBOTTEST'],stall_warnings=True,is_async=True)

#Setups up Flask Web Server
app = Flask(__name__)

@app.route('/')
def home():
    return "EE to English Converter"

app.run(host='0.0.0.0', port=os.environ.get('PORT'))

#Runs Stream Listener
while True:
    try:
        stream.filter(follow=os.environ["FOLLOW"].split(),track=os.environ["TRACK"].split(),stall_warnings=True)
    except (ProtocolError) as e:
        print(e)
        continue
    except Exception as e:
        print(e)
        continue
