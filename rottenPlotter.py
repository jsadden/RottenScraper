import matplotlib.pyplot as plot

#get and open data file
DATAFILE = 'rottenScraperData.txt'
rottenFile = open(DATAFILE, 'r')
DELIMITER = '\t'

#read the headers in the first line
headers = rottenFile.readline().strip().split(DELIMITER)

#dictionaries which will contain the genre's counted movies, the sum of the gaps in score, and the average gap
GENRECOUNT = {}
GENREGAPSUM = {}
GENREGAPAVG = {}

for line in rottenFile:
    #read the line and extract ratings data
    words = line.strip().split(DELIMITER)
    criticRating = words[1].strip('%')
    userRating = words[3].strip('%')
    genre = words[5]

    #if both ratings exist numerically, calculate ratings gap, else go to next line
    if criticRating.isnumeric() and userRating.isnumeric():
        ratingGap = abs(int(criticRating) - int(userRating))

    else:
        continue

    #check if genre is present in dictionary, add to count and sum if it is, init if it isn't, 
    if genre in GENRECOUNT:
        GENRECOUNT[genre] += 1
        GENREGAPSUM[genre] += ratingGap
    else:
        GENRECOUNT[genre] = 1
        GENREGAPSUM[genre] = ratingGap


#close the file
rottenFile.close()

#calculate averages
for genre in GENREGAPSUM:
    GENREGAPAVG[genre] = GENREGAPSUM[genre] / GENRECOUNT[genre]

#sort average dictionary
GENREGAPAVG = {k: v for k, v in sorted(GENREGAPAVG.items(), key=lambda item: item[1])}

#plot data
plot.bar(range(len(GENREGAPAVG)), list(GENREGAPAVG.values()), width=0.8, tick_label=list(GENREGAPAVG.keys()))
plot.xlabel('Genre')
plot.ylabel('Average Gap')
plot.title('Average Gaps in Critic and User Scores by Genre on Rotten Tomatoes')
plot.xticks(rotation=90)
plot.tight_layout()
plot.show()
