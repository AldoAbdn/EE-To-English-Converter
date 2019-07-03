import tweepy
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import urllib3.request
from bs4 import BeautifulSoup

class StreamListener(tweepy.StreamListener):
    """Subclass of Tweepy SteamListener for reading URL articles 

    Custom SteamListener for accessing twitters streaming API and reading
    articles, replies to original tweet with contents of article 

    Attributes: 
        api: An object that contains twitter API object 
        appendage: A String that is added to the end of tweet segments
        hashtags: A String that is added to the end of tweet segments with hashtags
        tweet_size: An Integer that is the length of each tweet segment  
    """

    def __init__(self, api, appendage='. ',hashtags='',tweet_size=280):
        """init 

        Initialises SteamListener

        Args:
            self: An object that represents instance 
            api: An object that contains twitter API object 
            appendage: A String that is added to the end of tweet segments
            hashtags: A String that is added to the end of tweet segments with hashtags
            tweet_size: An Integer that is the length of each tweet segment 

        Returns:
            A custom tweepy stream listener 
        """
        super(StreamListener)
        self.api = api
        self.appendage = appendage
        self.hashtags = hashtags
        self.tweet_size = tweet_size

    def on_status(self,status):
        """Status event handler 

        Called when listener detects a new status has been posted, calls 
        convert tweet to read tweet 

        Args: 
            self: An object that represents instance 
            status: An object that represents a tweet 
        """
        self.convertTweet(status)

    def on_error(self, status_code):
        """Error event handler 

        Called when an error occurs. returns twitter api status code 
        prints status code 

        Args: 
            self: An object that represents instance 
            status_code: An integer representing twitter api status code
        """
        print(status_code)

    def convertTweet(self,status):
        """Reads articles from URL within a tweet 

        Reads the first URL within a tweet and replies to status with text from article

        Args: 
            self: An object that represents instance 
            status: An object that represents a tweet 
        """
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
