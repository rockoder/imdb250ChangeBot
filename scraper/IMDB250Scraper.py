from lxml import html
import requests
from movie import Movie

def imdb250Scrape(isSimulate, nTopMovies, src):
    tree = None

    if isSimulate is True:
        tree = html.parse(src)
    else:
        page = requests.get(src) #'http://www.imdb.com/chart/top'
        tree = html.fromstring(page.content)

    return scrape(tree, nTopMovies, src)

def scrape(tree, nTopMovies, src):
    urls = tree.xpath('//*[@id="main"]/div/span/div/div/div[3]/table/tbody/tr[*]/td[@class="titleColumn"]/a')
    titles = tree.xpath('//*[@id="main"]/div/span/div/div/div[3]/table/tbody/tr[*]/td[@class="titleColumn"]/a/text()')
    ratings = tree.xpath('//*[@id="main"]/div/span/div/div/div[3]/table/tbody/tr[*]/td[@class="ratingColumn imdbRating"]/strong/text()')

    imdbTop250Movies = []

    for i in range(0, nTopMovies):
        imdbTop250Movies.append(Movie.Movie(ratings[i], titles[i], "http://imdb.com" + urls[i].attrib['href']))

    return imdbTop250Movies
