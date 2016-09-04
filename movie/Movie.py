class Movie:

    def __init__(self, movieRating, movieName, movieURL):
        self.movieRating = movieRating
        self.movieName = movieName
        self.movieURL = movieURL

    def __str__(self):
    	return self.movieRating + " " + self.movieName
