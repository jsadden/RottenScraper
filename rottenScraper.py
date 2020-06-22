#------------------------------------------------------------
#written by Jim Sadden
#script to scrape Rotten Tomatoes for user and critic ratings
#------------------------------------------------------------
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import math

BASEURL = 'https://www.rottentomatoes.com'

#dictionary containing each genre and its associated number to be inserted into the URL
GENRES = {
    'action': 1,
    'animation': 2,
    'art & foreign': 4,
    'classics': 5,
    'comedy': 6,
    'documentary': 8,
    'drama': 9,
    'horror': 10,
    'kids & family': 11,
    'mystery': 13,
    'romance': 18,
    'sci-fi & fantasy': 14
}

#path to chrome and init of selenium webdriver
PATH = 'C:/Users/jsadd/Desktop/Learning Python/chromedriver.exe'
driver = webdriver.Chrome(PATH)

#time intervals for sleeping and webdriver timeout
URLSLEEPINTERVAL = 0.5
CLICKSLEEPINTERVAL = 3
TIMEOUTINTERVAL = 10

#constants defining movies to be scraped each page and the number of movies displayed per 'load more' click
MOVIECOUNTPERGENRE = 60
MOVIESPERCLICK = 32

#create, open, and write to data file
rottenFile = open('rottenScraperData.txt', 'w')
DELIMITER = '\t'
movieDataHeaders = ['Movie Title', 'Critic Rating', 'Critic Rating Count', 'User Rating', 'User Rating Count', 'Genre']
rottenFile.write(DELIMITER.join(movieDataHeaders) + '\n')


#loop over each genre
for genre in GENRES:

    #build and get URL per genre
    GENREURL = f'/browse/dvd-streaming-all?minTomato=0&maxTomato=100&services=amazon;hbo_go;itunes;netflix_iw;vudu;amazon_prime;fandango_now&genres={str(GENRES[genre])}&sortBy=release'
    driver.get(BASEURL + GENREURL)

    try:
        #wait for page load
        element = WebDriverWait(driver, TIMEOUTINTERVAL).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'mb-movie'))
        )

        #get total movie count in a genre
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        genreTotalMovieCount = soup.find(id='count-link').text.split(' ')[3].strip()

        #determine how many 'load more' button clicks are required to scrape the number of movies requested
        #checks to ensure that total movie count is not exceeded in the request --> caps it if it does exceed
        clicksRequired = 0
        if MOVIECOUNTPERGENRE > int(genreTotalMovieCount):
            clicksRequired = math.floor(int(genreTotalMovieCount) / MOVIESPERCLICK)
        else:
            clicksRequired = math.floor(MOVIECOUNTPERGENRE / MOVIESPERCLICK)

        #checks for 'load more' button and clicks it as many times as determined above
        for i in range(clicksRequired):
            try:
                loadMoreButton = WebDriverWait(driver, TIMEOUTINTERVAL).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'mb-load-btn'))
                )
                loadMoreButton.click()
                time.sleep(CLICKSLEEPINTERVAL)
            except Exception as e:
                print(e)
                continue
        
        #get the movies
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        movies = soup.find_all('div', class_='movie_info')

        movieCount = 0
        for movie in movies:

            #checks to see if requested scraping limit has been reached and move to next genre if so
            movieCount += 1
            if movieCount > MOVIECOUNTPERGENRE:
                break

            #get movie title
            movieTitle = movie.find('h3', class_='movieTitle').text.strip()
            
            #get movie page
            movieURL = movie.find('a')['href']
            moviePage = requests.get(BASEURL + movieURL)
            time.sleep(URLSLEEPINTERVAL)
            movieSoup = BeautifulSoup(moviePage.content, 'html.parser')

            #get movie critic ratings
            criticSection = movieSoup.find('div', class_='mop-ratings-wrap__half')
            criticRating = criticSection.find('span', class_='mop-ratings-wrap__percentage')
            criticRatingCount = criticSection.find('small', class_='mop-ratings-wrap__text--small')
            if criticRating:
                criticRating = criticRating.text.strip()
                criticRatingCount = criticRatingCount.text.strip()
            else:
                criticRating = 'NOT FOUND'
                criticRatingCount = 'NOT FOUND'
                
            #get movie user ratings
            userSection = movieSoup.find('div', class_='audience-score')
            userRating = userSection.find('span', class_='mop-ratings-wrap__percentage')
            userRatingCount = userSection.find('strong', class_='mop-ratings-wrap__text--small')
            if userRating:
                userRating = userRating.text.strip()
                userRatingCount = userRatingCount.text.split(':')[1].strip()
            else:
                userRating = 'NOT FOUND'
                userRatingCount = 'NOT FOUND'
            

            #uncomment to print movie info
            # print(movieTitle)
            # print(movieURL)
            # print('Critic Rating: ' + criticRating)
            # print('Critic Rating Count: ' + criticRatingCount)
            # print('User Rating: ' + userRating)
            # print('User Rating Count: ' + userRatingCount)
            #print('GENRE: ' + genre)
            # print('\n')

            #write movie data to file
            movieData = [movieTitle, criticRating, criticRatingCount, userRating, userRatingCount, genre]
            rottenFile.write(DELIMITER.join(movieData) + '\n')
            time.sleep(URLSLEEPINTERVAL)

    except Exception as e:
        print(e)
        continue


print('finished')
rottenFile.flush()
rottenFile.close()
driver.quit()
