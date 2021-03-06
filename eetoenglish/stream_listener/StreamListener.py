from __future__ import unicode_literals
from nltk import tokenize
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

    def __init__(self, api, appendage=' ', hashtags='', tweet_size=280):
        """init 

        Initialises SteamListener

        Args:
            self: An object that represents instance 
            api: An object that contains twitter API object 
            appendage: A String that is added to the end of tweet segments
            hashtags: A String that is added to the end of tweet segments with hashtags
            tweet_size: An Integer that is the length of each tweet segment 
            tweet_intro: A String that holds the initial tweet to be sent

        Returns:
            A custom tweepy stream listener 
        """
        super(StreamListener)
        self.api = api
        self.appendage = appendage
        self.hashtags = hashtags
        self.tweet_size = tweet_size
        self.tweet_intro = "This tweet was generated by EE-To-English-Converter: github.com/AldoAbdn/EE-To-English-Converter using content created by the Evening Express. Any issues with this thread, please tweet at @AldoAbdn"
        self.tweet_signature = "https://www.eveningexpress.co.uk/subscribe/"

    def on_status(self, status):
        """Status event handler 

        Called when listener detects a new status has been posted, calls 
        convert tweet to read tweet 

        Args: 
            self: An object that represents instance 
            status: An object that represents a tweet 
        """
        #Filters out retweets, replies and self
        if(not self.isReply(status) and (self.api.me().id != status.user.id)):
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

    def convertTweet(self, status):
        """Reads articles from URL within a tweet 

        Reads the first URL within a tweet and replies to status with text from article

        Args: 
            self: An object that represents instance 
            status: An object that represents a tweet 
        """
        #Tries to get a valid URL
        try:
            url = status.entities['urls'][0]['url']
        except IndexError:
            return
        #Convert content into tweets
        retry = 3
        jserror = "We've detected that JavaScript is disabled in your browser."
        sentences = ["We've detected that JavaScript is disabled in your browser."]
        while jserror in sentences and retry > 0:
            content = self.getHTMLContent(url)
            sentences = self.splitIntoSentences(content)
            retry -= 1
        if retry != 0:
            self.createTweets(sentences, status)
        elif jserror in sentences:
            print("Error for URL:" + url)

    def getHTMLContent(self, url):
        """Parses html body and returns it

        Takes in a url, fetches the html and then returns the first div that has the right class

        Args: 
            self: An object that represents instance
            url: A string that contains a URL

        Returns:
            An object that represents the DOM of the HTML document 
        """
        response = urllib3.PoolManager().request("GET",url)
        parsed_html = BeautifulSoup(response.data.decode('utf-8'),features="html.parser")
        return parsed_html

    def splitIntoSentences(self, content):
        """Splits Paragraphs into sentences

        Loops through paragraphs and then splits it into sentenes to be combined into tweets later

        Args: 
            self: An object that represents instance
            content: An object that represents DOM of HTML doc

        Returns:
            An list of strings 
        """
        #Get all paragraphs (with no css class)
        try:
            paragraphs = content.find_all('p',{'class':None})
        except AttributeError:
            return
        content_string = ""
        for p in paragraphs:
            content_string += p.text + " "
        sentences = tokenize.sent_tokenize(content_string)
        return self.splitLargeSentences(sentences)

    def splitLargeSentences(self, sentences):
        """Splits sentences larger than tweet size

        Takes in the split sentences and checks if they are larger than a tweet, splits into smaller parts are adds to list

        Args:
            self: An object that represents instance
            sentences: original sentence list

        Returns:
            A list of strings
        """
        sentence_index = 0
        while(sentence_index < (len(sentences))):
            if len(sentences[sentence_index]) >= self.tweet_size:
                    sentence = sentences.pop(sentence_index)
                    split_sentences = self.splitSentence(sentence)
                    #Add sentences to original list 
                    for x in range(len(split_sentences)):
                        sentences.insert(sentence_index + x,split_sentences[x])
                    sentence_index += len(split_sentences)
            else: 
                sentence_index+=1
        return sentences

    def createTweets(self, sentences, status):
        """Combines sentences into tweets and posts them

        Combines sentences into tweets, sends out complete tweets

        Args: 
            self: An object that represents instance
            sentences: A list of string sentences
            status: An Object representing a tweet
        """
        if sentences is None:
            return
        status = self.postIntroTweet(status)
        tweet = ""
        sentence_index = 0
        #While we haven't gone through all the sentences 
        while sentence_index < (len(sentences)):
            #If sentence + appendage is not greater than tweet size
            if len(tweet) + len(sentences[sentence_index]) + len(self.appendage) <= self.tweet_size:
                tweet+=sentences[sentence_index]+self.appendage
                sentence_index+=1
            #Else if sentence itself is short enough
            elif len(tweet) + len(sentences[sentence_index]) <= self.tweet_size:
                tweet+=sentences[sentence_index]
                sentence_index+=1
            #Else if the combined size is greater than the tweet size, start a new tweet 
            elif len(tweet) + len(sentences[sentence_index]) > self.tweet_size:
                #If there is room, add hashtags to end
                if len(tweet)+len(self.hashtags)<self.tweet_size:
                    tweet += self.hashtags
                status = self.postTweet(tweet, status.id)
                tweet=""
        status = self.postSignatureTweet(tweet, status)

    def postIntroTweet(self, status):
        """Posts first tweet

        Posts the first tweet in the thread that contains the quoted tweet

        Args: 
            self: An object that represents instance
            status: The original tweet that triggered the bot
        
        Returns:
            Status
        """
        #Intro quoted tweet
        tweet = "https://twitter.com/" + str(status.user.id) + "/status/" + str(status.id) + " " + self.tweet_intro + " " + self.hashtags
        return self.postTweet(tweet)

    def postSignatureTweet(self, tweet, status):
        """Posts final tweet

        Posts the final tweet in the thread 

        Args:
            self: An object that represents instance
            status: last status that was posted

        Returns:
            Status
        """
        #If there is enough room at signature to end
        if len(tweet)+len(self.tweet_signature)+len(self.appendage) <= self.tweet_size :
            tweet+=self.appendage+self.tweet_signature
            return self.postTweet(tweet, status.id)
        #else post seperatly
        else:
            status = self.postTweet(tweet, status.id)
            return self.postTweet(self.tweet_signature, status.id)


    def postTweets(self, tweets, reply_id):
        """Posts tweets to twitter

        Posts tweets to twitter as a reply to the original in a thread 

        Args: 
            self: An object that represents instance
            tweets: A list of strings representing tweets
            reply_id: A string representing an id of a tweet the new tweet is a reply to
        """
        for tweet in tweets:
            try:
                status = self.postTweet(tweet, reply_id)
                reply_id = status.id
            except tweepy.error.TweepError as e:
                print(e)
                print(tweet + "ERROR")
            except UnicodeDecodeError as e:
                print(e)
                print(tweet + "UNICODE_DECODE_ERROR")
            except UnicodeEncodeError as e:
                print(e)
                print(tweet + "UNICODE_ENCODE_ERROR")

    def postTweet(self, tweet, reply_id=None):
        """Posts a tweet to twitter

        Posts a tweet to twitter with an optional ID of a tweet it should be a reply to

        Args: 
            self: An object that represents instance
            tweet: An object representing a tweet 
            reply_id: A string representing an id of a tweet the new tweet is a reply to
        """
        try:
            status = self.api.update_status(status=tweet.encode('utf-8'), in_reply_to_status_id=reply_id)
            return status
        except tweepy.error.TweepError as e:
            print(e)
            print(tweet + "ERROR")
        except UnicodeDecodeError as e:
            print(e)
            print(tweet + "UNICODE_DECODE_ERROR")
        except UnicodeEncodeError as e:
            print(e)
            print(tweet + "UNICODE_ENCODE_ERROR")

    def isReply(self, status):
        """Checks if a status is a reply

        Checks attributes of status object for any that can identify it as a reply

        Args: 
            self: An object that represents instance
            status: An object that represents a tweet 
        """
        if(status.retweeted or status.in_reply_to_status_id or status.in_reply_to_status_id_str or status.in_reply_to_user_id or status.in_reply_to_user_id_str or status.in_reply_to_screen_name or status.text.startswith('RT')):
            return True
        else:
            return False

    def splitSentence(self, sentence):
        """Splits sentences into smaller chunks 

        Splits a long sentence into single worlds and combines the words into shorter sentences that can be tweeted 

        Args: 
            self: An object that represents instance
            sentence: An String that represents a sentence 

        Returns:
            An list of strings 
        """
        words = sentence.split()
        split_sentences = [""]
        split_index = 0
        #Put words into new sentences
        for word in words:
            #First Word
            if(len(split_sentences[split_index])==0):
                split_sentences[split_index] += word
            #Rest of Words
            elif(len(split_sentences[split_index])+len(word)+1<self.tweet_size):
                split_sentences[split_index] += " " + word
            #Start new sentence
            else:
                split_index+=1
                split_sentences.append(word)
        return split_sentences