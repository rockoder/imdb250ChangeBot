from lxml import html
import requests
import difflib
import sys
import config
import twitter
import sched
import time
from datetime import datetime

isSimulate = False
loopTimeSec = 15 * 60 # 60 mins

class Movie:

    def __init__(self, movieRating, movieName):
        self.movieRating = movieRating
        self.movieName = movieName

    def __str__(self):
    	return self.movieRating + " " + self.movieName

def getMovieList(movieList):
	return "\n".join((str(movie) for movie in movieList))

def fakeFromFile(fileName):
	imdbTop250Movies = []
	fOld = open(fileName, 'r')

	for r in fOld.readlines():
		imdbTop250Movies.append(Movie(r[0:3], r[4:-1	]))

	return imdbTop250Movies

def getNew():

	tree = None

	if isSimulate is True:
		print "simulation"
		tree = html.parse("page.html")
	else:
		page = requests.get('http://www.imdb.com/chart/top')
		tree = html.fromstring(page.content)

	urls = tree.xpath('//*[@id="main"]/div/span/div/div/div[3]/table/tbody/tr[*]/td[@class="titleColumn"]/a')
	titles = tree.xpath('//*[@id="main"]/div/span/div/div/div[3]/table/tbody/tr[*]/td[@class="titleColumn"]/a/text()')
	ratings = tree.xpath('//*[@id="main"]/div/span/div/div/div[3]/table/tbody/tr[*]/td[@class="ratingColumn imdbRating"]/strong/text()')

	imdbTop250MoviesNew = []

	for i in range(0, 250):
		imdbTop250MoviesNew.append(Movie(ratings[i].encode("utf-8"), titles[i].encode("utf-8")))

	return imdbTop250MoviesNew

def PostTweet(twitterApi, tweet, attempt):
	# No tweet in debug mode
	if isSimulate is True:
		print "Simulate tweeting: " + tweet
	else:
		try:
			# TODO: Check tweet length
			print "Real tweeting: " + tweet
			twitterApi.PostUpdate(tweet)
		except Exception as e:
			print "Error while tweeting: %s\n" % e
			if attempt == 1:
				tweet = tweet + " Time " + str(datetime.strftime(datetime.now(), '%H:%M:%S'))
				print "Tweeting with time appended: %s" % tweet
				PostTweet(twitterApi, tweet, 2)

def getOpt():
	if len(sys.argv) > 1:
		if sys.argv[1] == 'simulate':
			global isSimulate
			isSimulate = True
			
			global loopTimeSec
			loopTimeSec = 3 # 3 sec

	print "isSumlate " + str(isSimulate)
	print "loopTimeSec " + str(loopTimeSec)

def processLoop(imdbTop250MoviesOld, sc):
	print str(datetime.now()) + ": processLoop"

	if isSimulate is True:
		imdbTop250MoviesNew = fakeFromFile("testNew")
		# print getMovieList(imdbTop250MoviesNew)
		# print "**************************"
	else:
		imdbTop250MoviesNew = getNew()

	d = difflib.Differ()
	diff = d.compare(getMovieList(imdbTop250MoviesOld).splitlines(1), getMovieList(imdbTop250MoviesNew).splitlines(1))

	# print '\n'.join(diff) # Has side effet of clearing the diff list
	# print "**************************"

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
			print "Old:\t%d: %s" % (lineNumOld, line[2:].strip())
			lineNumOld += 1

		if code == "+ ":
			imdbTop250MoviesNewDiff.append(lineNumNew - 1)
			print "New:\t%d: %s" % (lineNumNew, line[2:].strip())
			lineNumNew += 1

		if code == "? ":
			pass

	# print imdbTop250MoviesOldDiff
	# print "**************************"
	# print imdbTop250MoviesNewDiff

	twitterApi = twitter.Api(config.consumer_key, config.consumer_secret, config.access_token, config.access_token_secret)

	for indexOld in list(imdbTop250MoviesOldDiff): # list() -- required because elements are removed from the org list
		movieName = imdbTop250MoviesOld[indexOld].movieName

		for indexNew in list(imdbTop250MoviesNewDiff): # list() -- required because elements are removed from the org list
			if imdbTop250MoviesNew[indexNew].movieName == movieName:

				# Movie rank increased
				if indexOld < indexNew:
					tweet = "Movie '%s' slipped from rank %d to rank %d." % (movieName, indexOld + 1, indexNew + 1)
					PostTweet(twitterApi, tweet, 1)

				if indexOld > indexNew:
					#  just ahead of %s -- imdbTop250MoviesNew[indexNew + 1].movieName -- add check of index range to be safe
					tweet = "Movie '%s' jumped from rank %d to rank %d." % (movieName, indexOld + 1, indexNew + 1)
					PostTweet(twitterApi, tweet, 1)

				imdbTop250MoviesOldDiff.remove(indexOld)
				imdbTop250MoviesNewDiff.remove(indexNew)

	for indexOld in imdbTop250MoviesOldDiff:
		movieName = imdbTop250MoviesOld[indexOld].movieName
		tweet = "Movie '%s' dropped from out of IMDb Top 250 from rank %d." % (movieName, indexOld + 1)
		PostTweet(twitterApi, tweet, 1)

	for indexNew in imdbTop250MoviesNewDiff:
		movieName = imdbTop250MoviesNew[indexNew].movieName
		# just ahead of %s -- imdbTop250MoviesNew[indexNew + 1].movieName -- handle index out of range
		tweet = "Movie '%s' got added to IMDb Top 250 at rank %d." % (movieName, indexNew + 1)
		PostTweet(twitterApi, tweet, 1)

	sc.enter(loopTimeSec, 1, processLoop, (imdbTop250MoviesNew, sc,))

def main():
	getOpt()

	if isSimulate is True:
		imdbTop250MoviesOld = fakeFromFile("testOld")
		# print getMovieList(imdbTop250MoviesOld)
		# print "**************************"
	else:
		imdbTop250MoviesOld = getNew()

	s = sched.scheduler(time.time, time.sleep)
	s.enter(loopTimeSec, 1, processLoop, (imdbTop250MoviesOld, s,))
	s.run()

if __name__ == "__main__":
    main()