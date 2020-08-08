#Deletes a thread of tweets 
from dotenv import load_dotenv 
load_dotenv()
import os
import tweepy
from eetoenglish.stream_listener.StreamListener import StreamListener
from urllib3.exceptions import ProtocolError

#Setup Auth
auth = tweepy.OAuthHandler(os.environ["CONSUMER_TOKEN"], os.environ["CONSUMER_SECRET"])
auth.set_access_token(os.environ["KEY"], os.environ["SECRET"])

#Twitter API
api = tweepy.API(auth)

#ID of end of thread 
delete_id = input("Tweet ID: ")
tweet = api.get_status(delete_id)
reply_id = ""

#Loop through and delete thread 
while (reply_id!=None):
    reply_id = tweet.in_reply_to_status_id_str
    api.destroy_status(tweet.id)
    tweet = api.get_status(reply_id)

