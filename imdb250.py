from lxml import html
from lxml import etree
import requests
import difflib
import sys

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

	tree = html.parse("page.html")

	if len(sys.argv) == 1:
		print "release"
		page = requests.get('http://www.imdb.com/chart/top')
		tree = html.fromstring(page.content)
	else:
		print "debug"

	urls = tree.xpath('//*[@id="main"]/div/span/div/div/div[3]/table/tbody/tr[*]/td[@class="titleColumn"]/a')
	titles = tree.xpath('//*[@id="main"]/div/span/div/div/div[3]/table/tbody/tr[*]/td[@class="titleColumn"]/a/text()')
	ratings = tree.xpath('//*[@id="main"]/div/span/div/div/div[3]/table/tbody/tr[*]/td[@class="ratingColumn imdbRating"]/strong/text()')

	imdbTop250MoviesNew = []

	for i in range(0, 250):
		imdbTop250MoviesNew.append(Movie(ratings[i].encode("utf-8"), titles[i].encode("utf-8")))

	return imdbTop250MoviesNew

imdbTop250MoviesOld = fakeFromFile("testOld")
# print getMovieList(imdbTop250MoviesOld)
# print "**************************"

imdbTop250MoviesNew = fakeFromFile("testNew") # getNew()
# print getMovieList(imdbTop250MoviesNew)
# print "**************************"

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

print imdbTop250MoviesOldDiff
print "**************************"
print imdbTop250MoviesNewDiff

for indexOld in list(imdbTop250MoviesOldDiff): # list() -- required because elements are removed from the org list
	movieName = imdbTop250MoviesOld[indexOld].movieName

	for indexNew in list(imdbTop250MoviesNewDiff): # list() -- required because elements are removed from the org list
		if imdbTop250MoviesNew[indexNew].movieName == movieName:

			# Movie rank increased
			if indexOld < indexNew:
				print "Movie '%s' slipped from rank %d to rank %d." % (movieName, indexOld + 1, indexNew + 1)

			if indexOld > indexNew:
				print "Movie '%s' jumped from rank %d to rank %d just ahead of %s" % (movieName, indexOld + 1, indexNew + 1, imdbTop250MoviesNew[indexNew + 1].movieName)

			imdbTop250MoviesOldDiff.remove(indexOld)
			imdbTop250MoviesNewDiff.remove(indexNew)

for indexOld in imdbTop250MoviesOldDiff:
	movieName = imdbTop250MoviesOld[indexOld].movieName
	print "Movie '%s' dropped from out of IMDb Top 250 from rank %d." % (movieName, indexOld + 1)

for indexNew in imdbTop250MoviesNewDiff:
	movieName = imdbTop250MoviesNew[indexNew].movieName
	print "Movie '%s' got added to IMDb Top 250 at rank %d just ahead of %s" % (movieName, indexNew + 1, imdbTop250MoviesNew[indexNew + 1].movieName)
