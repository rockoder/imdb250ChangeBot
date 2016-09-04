from config import config
from mytwitter.TwitterApiFactory import TwitterApiFactory

def main():
    ti = TwitterApiFactory.getTwitterApi(config)

    ti.PostUpdate("sample ↑ tweet")

if __name__ == "__main__":
    main()
