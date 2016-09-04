from mytwitter import TwitterInterface

class TwitterImpl(TwitterInterface.TwitterInterface):

    def __init__(self, fp):
        self.fp = fp

    def PostUpdate(self, tweet):
        self.fp.write(tweet)
        self.fp.write("\n")
