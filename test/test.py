import tweepy
from eetoenglish.StreamListener import StreamListener

auth = tweepy.OAuthHandler("6Ft1pIy6lvQehU54D4nDdU0gC", "jOJbnxQ2oFfm5XrorWqEcdIHJm1c0doOSpmBFrkuK7NkC16Oui")
auth.set_access_token("853735939730010112-McGaH2C5eOKHO9zr520fXonjSJanRcq", "LzkagKu6oaMAjAgsGtfNrHRhABlbi266AGgeL1JBqTNMa")

api = tweepy.API(auth)

streamlistener = StreamListener(api)
stream = tweepy.Stream(auth=api.auth, listener=streamlistener)
stream.filter(follow=['19765204','853735939730010112'],track=['#EEBOTTEST'])



 





