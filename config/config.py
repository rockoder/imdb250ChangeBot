# Set Twitter configs here
consumer_key=''
consumer_secret=''
access_token=''
access_token_secret=''

# Run program in simulation mode
isSimulate = False

# Time interval to check the change in imdb
loopTimeSec = 15 * 60 # 15 mins

# Log file
# need separate files for log file and tweet simulation file
fp = open('imdb250.log', 'a')

nTopMovies = 250