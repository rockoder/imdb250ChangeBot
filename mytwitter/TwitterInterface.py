from abc import ABCMeta, abstractmethod
import twitter

class TwitterInterface(metaclass=ABCMeta):
    @abstractmethod
    def PostUpdate(self, tweet):
        pass

TwitterInterface.register(twitter.api.Api)