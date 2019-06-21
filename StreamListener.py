import tweepy
import urllib3.request
from bs4 import BeautifulSoup

class StreamListener(tweepy.StreamListener):
    def __init__(self, api, appendage='. '):
        super(StreamListener)
        self.api = api
        self.appendage = appendage
        self.hashtags = '#Aberdeen #News'
        self.tweet_size = 280

    def on_status(self,status):
        self.convertTweet(status)

    def on_error(self, status_code):
        print(status_code);

    def convertTweet(self,status):
        tweet_id = status.id
        try:
            url = status.entities['urls'][0]['url']
        except IndexError:
            return
        response = urllib3.PoolManager().request("GET",url)
        parsed_html = BeautifulSoup(response.data.decode('utf-8'),features="html.parser")
        content = parsed_html.body.find('div', attrs={'class':'lightbox-content'})
        try:
            paragraphs = content.find_all('p')
        except AttributeError:
            return
        content_string = ""
        for p in paragraphs:
            content_string += p.text
        sentences = content_string.split(".")
        tweets = []
        sentence_index = 0
        tweet_index = 0
        while sentence_index < (len(sentences)-1):
            if len(tweets)==tweet_index:
                tweets.insert(tweet_index,sentences[sentence_index]+self.appendage)
                sentence_index+=1
            elif len(tweets[tweet_index]) + len(sentences[sentence_index]) + len(self.appendage) > self.tweet_size:
                if len(tweets[tweet_index])+len(self.hashtags)<self.tweet_size:
                    tweets[tweet_index] += self.hashtags
                tweet_index += 1
            else:
                tweets[tweet_index] += sentences[sentence_index]+self.appendage
                sentence_index += 1
        tweets.append(self.hashtags)
        for tweet in tweets:
            try:
                status = self.api.update_status(tweet, in_reply_to_status_id=tweet_id)
            except tweepy.error.TweepError:
                print(tweet)
            tweet_id = status.id
