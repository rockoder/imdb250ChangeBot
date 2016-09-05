import sys
import os
import re
import sched
import time
from datetime import datetime
import string

import difflib
import twitter

from scraper.IMDB250Scraper import imdb250Scrape
from mytwitter.TwitterApiFactory import TwitterApiFactory
from config import config

def getMovieList(movieList):
    return "\n".join((str(movie) for movie in movieList))

def postTweet(twitterApi, tweet, attempt):
    if len(tweet) > config.tweetLength:
        config.fp.write("Tweet length %s greater than %s:%s" % len(tweet), config.tweetLength, tweet)
        return

    try:
        # TODO: Check tweet length
        twitterApi.PostUpdate(tweet)
    except Exception as e:
        config.fp.write("Error while tweeting: %s\n" % e)
        if attempt == 1:
            tweet = tweet + " Time " + str(datetime.strftime(datetime.now(), '%H:%M:%S'))
            config.fp.write("Tweeting with time appended: %s\n" % tweet)
            postTweet(twitterApi, tweet, 2)

def getDiffIndex(diff):
    lineNumOld = 1
    lineNumNew = 1
    imdbTop250MoviesOldDiff = []
    imdbTop250MoviesNewDiff = []

    for line in list(diff):
        code = line[:2]

        if code == "  ":
            lineNumOld += 1
            lineNumNew += 1

        if code == "- ":
            imdbTop250MoviesOldDiff.append(lineNumOld - 1)
            config.fp.write("Old:\t%d: %s\n" % (lineNumOld, line[2:].strip()))
            lineNumOld += 1

        if code == "+ ":
            imdbTop250MoviesNewDiff.append(lineNumNew - 1)
            config.fp.write("New:\t%d: %s\n" % (lineNumNew, line[2:].strip()))
            lineNumNew += 1

        if code == "? ":
            pass

    return imdbTop250MoviesOldDiff, imdbTop250MoviesNewDiff

def generateHashTag(movieName):
    tempMovieName = movieName
    tempMovieName = tempMovieName.replace("'", "")
    tempMovieName = tempMovieName.replace("\"", "")
    # · Required for Wall·E
    return "#" + "".join([string.capwords(x.strip()) for x in re.split(';|,|\s+|#|-|:|·', tempMovieName)])

def generateTweet(imdbTop250MoviesOld, imdbTop250MoviesOldDiff, imdbTop250MoviesNew, imdbTop250MoviesNewDiff, twitterApi):
    combinedTweets = ""
    tweet = ""

    for indexOld in list(imdbTop250MoviesOldDiff): # list() -- required because elements are removed from the org list
        movieName = imdbTop250MoviesOld[indexOld].movieName

        for indexNew in list(imdbTop250MoviesNewDiff): # list() -- required because elements are removed from the org list
            if imdbTop250MoviesNew[indexNew].movieName == movieName and indexOld != indexNew:

                if indexOld < indexNew: # Movie rank increased. Movie went down in the chart.
                    tweet = "%s down from %d to %d. %s" % (movieName, indexOld + 1, indexNew + 1,
                                                              generateHashTag(movieName))
                elif indexOld > indexNew: # Movie rank decreased. Movie went up in the chart.
                    #  just ahead of %s -- imdbTop250MoviesNew[indexNew + 1].movieName -- add check of index range to be safe
                    tweet = "%s up from %d to %d. %s" % (movieName, indexOld + 1, indexNew + 1,
                                                            generateHashTag(movieName))

                if len(combinedTweets + tweet + "\n") <= config.tweetLength:
                    combinedTweets += tweet + "\n"
                else:
                    combinedTweets = combinedTweets[:-1]
                    postTweet(twitterApi, combinedTweets, 1)
                    combinedTweets = tweet + "\n"
                    tweet = ""

                imdbTop250MoviesOldDiff.remove(indexOld)
                imdbTop250MoviesNewDiff.remove(indexNew)

    if (len(combinedTweets) > 0):
        combinedTweets = combinedTweets[:-1]
        postTweet(twitterApi, combinedTweets, 1)

    for indexOld in imdbTop250MoviesOldDiff:
        movieName = imdbTop250MoviesOld[indexOld].movieName
        tweet = "%s dropped from out of IMDb Top 250 from rank %d. %s" % (movieName, indexOld + 1,
                                                                             generateHashTag(movieName))
        postTweet(twitterApi, tweet, 1)

    for indexNew in imdbTop250MoviesNewDiff:
        movieName = imdbTop250MoviesNew[indexNew].movieName
        # just ahead of %s -- imdbTop250MoviesNew[indexNew + 1].movieName -- handle index out of range
        tweet = "%s got added to IMDb Top 250 at rank %d. %s" % (movieName, indexNew + 1,
                                                                    generateHashTag(movieName))
        postTweet(twitterApi, tweet, 1)

def processLoop(imdbTop250MoviesOld, twitterApi, sc):
    config.fp.write(str(datetime.now()) + ": processLoop" + "\n")

    if config.isSimulate is True:
        imdbTop250MoviesNew = imdb250Scrape(config.isSimulate, config.nTopMovies, 'test' + os.sep + 'newpage.html')
    else:
        imdbTop250MoviesNew = imdb250Scrape(config.isSimulate, config.nTopMovies, 'http://www.imdb.com/chart/top')

    d = difflib.Differ()
    diff = d.compare(getMovieList(imdbTop250MoviesOld).splitlines(1),
                     getMovieList(imdbTop250MoviesNew).splitlines(1))

    imdbTop250MoviesOldDiff, imdbTop250MoviesNewDiff = getDiffIndex(diff)

    generateTweet(imdbTop250MoviesOld, imdbTop250MoviesOldDiff,
                  imdbTop250MoviesNew, imdbTop250MoviesNewDiff, twitterApi)

    config.fp.flush()

    sc.enter(config.loopTimeSec, 1, processLoop, (imdbTop250MoviesNew, twitterApi, sc,))

def getOpt():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'simulate':
            config.isSimulate = True
            config.loopTimeSec = 3 # 3 sec interval

    config.fp.write("isSumlate " + str(config.isSimulate) + "\n")
    config.fp.write("loopTimeSec " + str(config.loopTimeSec) + "\n")
    config.fp.flush()

def main():
    getOpt()

    if config.isSimulate is True:
        imdbTop250MoviesOld = imdb250Scrape(config.isSimulate, config.nTopMovies, 'test' + os.sep + 'oldpage.html')
    else:
        imdbTop250MoviesOld = imdb250Scrape(config.isSimulate, config.nTopMovies, 'http://www.imdb.com/chart/top')

    twitterApi = TwitterApiFactory.getTwitterApi(config)

    s = sched.scheduler(time.time, time.sleep)
    s.enter(config.loopTimeSec, 1, processLoop, (imdbTop250MoviesOld, twitterApi, s,))
    s.run()
    config.fp.close()

if __name__ == "__main__":
    main()
