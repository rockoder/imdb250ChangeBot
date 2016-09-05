from mytwitter import TwitterImpl
import twitter

class TwitterApiFactory:

    @staticmethod
    def getTwitterApi(config):
        if config.isSimulate:
            return TwitterImpl.TwitterImpl(config.fp)
        else:
            return twitter.Api(config.consumer_key,
                               config.consumer_secret,
                               config.access_token,
                               config.access_token_secret)
