# -*- coding: utf-8 -*-


import re
import io
import csv
import json
import time
import pickle
import tweepy as tw
import datetime
from tweepy import OAuthHandler

# API Keys
consumer_key = "XXX"
consumer_secret = "XXX"
access_token = "XXX"
access_token_secret = "XXX"

# API Settings
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
# create tweepy API object to fetch tweets
api = tw.API(auth)
api = tw.API(auth, wait_on_rate_limit=True)

###############################################################################

result = []
t_id = []


def get_tweets(query, count, gc):
    """
    Function for fetching tweet data per location
    :param query: Search keyword and conditions
    :param count: Number of tweets to get
    :param gc: geocoding, the geografical location to search
    :return: Tweets data, including the location information, full text, tweet_id, user_id, etc.
    """
    result = []
    t_id = pickle.load(open("tweetid.p", "rb"))
    # call twitter api to fetch tweets
    new_search = query + " -filter:retweets"
    fetched_tweets = tw.Cursor(api.search, new_search, tweet_mode='extended', lang='en', geocode=gc).items(count)
    time.sleep(5)

    for tweet in fetched_tweets:
        # empty dictionary to store required params of a tweet
        parsed_tweet = {}
        # saving text of tweet
        parsed_tweet['text'] = tweet.full_text
        if "http" not in tweet.full_text:  # Ignore the web links
            line = re.sub("[^A-Za-z]", " ", tweet.full_text)
            target.write(line + "\n")
            st = hasattr(tweet, 'retweeted_status')  # Check Status of tweets, If it is orignal tweet or a retweet

            created_at = tweet.created_at
            timestamp = int(created_at.replace(tzinfo=datetime.timezone.utc).timestamp())

            if tweet.user.location != None:  # Considering the tweets that have location information
                try:
                    pc = tweet.place.bounding_box.coordinates
                except:
                    pc = None

                obj = {
                    'text': tweet.full_text,
                    'timestamp': timestamp,
                    'tweet_id': tweet.id_str,
                    'user_id': tweet.user.id_str,
                    'user_followers': tweet.user.followers_count,
                    'is_rt': st,
                    # longitude,latitude
                    'coordinates': tweet.coordinates,
                    'user_location': tweet.user.location,
                    'favorites': tweet.favorite_count,
                    'retweets': tweet.retweet_count,
                    'lang': tweet.lang,
                    'place_coords': pc
                }
                # Checking the tweets id to avoid redundant saving
                if not (tweet.id_str in t_id):
                    t_id.append(tweet.id_str)
                    result.append(obj)

    pickle.dump(t_id, open("tweetid.p", "wb"))
    return result

    # creating object of TwitterClient Class
    # calling function to get tweets


###############################################################################
# Function for clearing memory during execution
# This function helps in clearing the tweets_id information file during runtime,
# this helps in fetching tweets from different location in one go.
def clearMem():
    t_id = []
    pickle.dump(t_id, open("tweetid.p", "wb"))


###############################################################################
# Function that calls the get_tweets function for particular tweets counts 
def extractandsave_data(q, g_code):
    tweets = get_tweets(query=q, count=1000000, gc=g_code)
    return tweets


# default geo_code is for the city of Madrid spain (our base case)
g_code = "40.4168,-3.7038,200km"


# This function pass query to extractandsave_data function
# Query refers to the search terms, in our case we considered covid, covid-19, COVID-19, corona, coronavirus
def extractCity(g_code):
    t1 = extractandsave_data("covid", g_code)
    time.sleep(5)
    t2 = extractandsave_data("covid-19", g_code)
    t3 = extractandsave_data("COVID-19", g_code)
    t4 = extractandsave_data("corona", g_code)
    t5 = extractandsave_data("coronavirus", g_code)
    time.sleep(5)

    t = t1 + t2 + t3 + t4 + t5  # All tweets are aggregated here and return by this function for saving to file
    return t


# From Here onward you can find the code block of per country or region.
# We consider multiple countries from Europe, Asia and also the main countries like UK,
# USA, Australia and search for major cities.
###############################################################################
# Spain
###############################################################################
clearMem()
city1 = extractCity("40.4168,-3.7038,200km")  # Madrid
json.dump({'tweets': city1}, open('tweetMadrid.json', 'w', encoding='utf-8'))
city2 = extractCity("41.398371,2.1741,200km")  # Barcelona
json.dump({'tweets': city2}, open('tweetBarcelona.json', 'w', encoding='utf-8'))
city3 = extractCity("37.382826,-5.973167,200km")  # Seville
json.dump({'tweets': city3}, open('tweetSeville.json', 'w', encoding='utf-8'))

clearMem()

city4 = extractCity("41.64531,-0.884861,200km")  # Zaragoza
json.dump({'tweets': city4}, open('tweetZaragoza.json', 'w', encoding='utf-8'))
city5 = extractCity("43.260919,-2.938764,200km")  # Bilbao
json.dump({'tweets': city5}, open('tweetBilbao.json', 'w', encoding='utf-8'))
city6 = extractCity("39.466667,-0.366667,200km")  # Velencia
json.dump({'tweets': city6}, open('tweetVelencia.json', 'w', encoding='utf-8'))
print("Spain Done.........!!")
###############################################################################
# Belgium
###############################################################################
clearMem()
city7 = extractCity("50.833333,4.33333,100km")  # Brussels
json.dump({'tweets': city7}, open('tweetBrussels.json', 'w', encoding='utf-8'))
city8 = extractCity("51.213886,4.401514,100km")  # Antwerp
json.dump({'tweets': city8}, open('tweetAntwerp.json', 'w', encoding='utf-8'))
city9 = extractCity("50.638674,5.570228,100km")  # Liege
json.dump({'tweets': city9}, open('tweetLiege.json', 'w', encoding='utf-8'))

clearMem()

city10 = extractCity("51.05,3.716667,100km")  # Ghent
json.dump({'tweets': city10}, open('tweetGhent.json', 'w', encoding='utf-8'))
city11 = extractCity("50.45527,3.951623,100km")  # Mons
json.dump({'tweets': city11}, open('tweetMons.json', 'w', encoding='utf-8'))
city12 = extractCity("51.210933,3.225971,100km")  # Brugge
json.dump({'tweets': city12}, open('tweetBrugge.json', 'w', encoding='utf-8'))
print("Belgium Done.........!!")
###############################################################################
# Italy
###############################################################################
clearMem()
city7 = extractCity("41.9,12.48333,200km")  # Rome
json.dump({'tweets': city7}, open('tweetRome.json', 'w', encoding='utf-8'))
city8 = extractCity("45.466667,9.2,200km")  # Milan
json.dump({'tweets': city8}, open('tweetMilan.json', 'w', encoding='utf-8'))
city9 = extractCity("45.05,7.66667,200km")  # Turin
json.dump({'tweets': city9}, open('tweetLiege.json', 'w', encoding='utf-8'))

clearMem()

city10 = extractCity("37.5,15.1,200km")  # Catania
json.dump({'tweets': city10}, open('tweetCatania.json', 'w', encoding='utf-8'))
city11 = extractCity("40.83333,14.25,200km")  # Naples
json.dump({'tweets': city11}, open('tweetNaples.json', 'w', encoding='utf-8'))
city12 = extractCity("45.438611,12.326667,200km")  # Venice
json.dump({'tweets': city12}, open('tweetVenice.json', 'w', encoding='utf-8'))
print("Italy Done.........!!")
###############################################################################
# Nethersland
###############################################################################
clearMem()
city7 = extractCity("52.35,4.916667,100km")  # Amsterdam
json.dump({'tweets': city7}, open('tweetAmsterdam.json', 'w', encoding='utf-8'))
city8 = extractCity("51.916667,4.5,100km")  # Rotterdam
json.dump({'tweets': city8}, open('tweetRotterdam.json', 'w', encoding='utf-8'))
city9 = extractCity("52.093813,5.119095,100km")  # Utrecht
json.dump({'tweets': city9}, open('tweetUtrecht.json', 'w', encoding='utf-8'))

clearMem()

city10 = extractCity("51.45,5.466667,100km")  # Eindhoven
json.dump({'tweets': city10}, open('tweetEindhoven.json', 'w', encoding='utf-8'))
city11 = extractCity("53.216667,6.55,100km")  # Groningen
json.dump({'tweets': city11}, open('tweetGroningen.json', 'w', encoding='utf-8'))
city12 = extractCity("52.505751,6.085822,100km")  # Zwolle
json.dump({'tweets': city12}, open('tweetZwolle.json', 'w', encoding='utf-8'))
print("Nethersland Done.........!!")
###############################################################################
# UK
###############################################################################
clearMem()
city7 = extractCity("51.514248,-0.093145,200km")  # London
json.dump({'tweets': city7}, open('tweetLondon1M.json', 'w', encoding='utf-8'))
city8 = extractCity("52.466667,-1.9166667,200km")  # Birmingham
json.dump({'tweets': city8}, open('tweetBirmingham.json', 'w', encoding='utf-8'))
city9 = extractCity("53.5,-2.216667,200km")  # Manchester
json.dump({'tweets': city9}, open('tweetManchester.json', 'w', encoding='utf-8'))

clearMem()

city10 = extractCity("53.8,-1.583333,200km")  # Leeds
json.dump({'tweets': city10}, open('tweetLeeds.json', 'w', encoding='utf-8'))
city11 = extractCity("55.833333,-4.25,200km")  # Glasgow
json.dump({'tweets': city11}, open('tweetGlasgow.json', 'w', encoding='utf-8'))
city12 = extractCity("51.514248,-0.093145,200km")  # London
json.dump({'tweets': city12}, open('tweetLondon.json', 'w', encoding='utf-8'))
print("UK Done.........!!")
###############################################################################
# #USA
###############################################################################
clearMem()
city7 = extractCity("33.753746,-84386330,200km")  # Atlanta
json.dump({'tweets': city7}, open('tweetAtlanta.json', 'w', encoding='utf-8'))
city8 = extractCity("40.730610,-73.935242,200km")  # NewYork
json.dump({'tweets': city8}, open('tweetNewYork.json', 'w', encoding='utf-8'))
city9 = extractCity("41.881832,-87.623177,200km")  # Chicago
json.dump({'tweets': city9}, open('tweetChicago.json', 'w', encoding='utf-8'))

clearMem()

city10 = extractCity("30.266666,-97.733330,200km")  # Austin
json.dump({'tweets': city10}, open('tweetAustin.json', 'w', encoding='utf-8'))
city11 = extractCity("37.773972,-122.431297,200km")  # Sanfrancisco
json.dump({'tweets': city11}, open('tweetSanfrancisco.json', 'w', encoding='utf-8'))
city12 = extractCity("47.608013,-122.335167,200km")  # Seattle
json.dump({'tweets': city12}, open('tweetSeattle.json', 'w', encoding='utf-8'))
print("USA Done.........!!")
###############################################################################
# #Europe
###############################################################################
clearMem()
city7 = extractCity("48.2,16.366667,100km")  # Vienna
json.dump({'tweets': city7}, open('tweetVienna.json', 'w', encoding='utf-8'))
city8 = extractCity("55.666667,12.583333,100km")  # Copenhagen
json.dump({'tweets': city8}, open('tweetCopenhagen.json', 'w', encoding='utf-8'))
city9 = extractCity("59.333333,18.05,100km")  # Stockholm
json.dump({'tweets': city9}, open('tweetStockholm.json', 'w', encoding='utf-8'))

clearMem()

city10 = extractCity("52.516667,13.4,100km")  # Berlin
json.dump({'tweets': city10}, open('tweetBerlin.json', 'w', encoding='utf-8'))
city11 = extractCity("50.11552,8.684167,100km")  # Frankfurt
json.dump({'tweets': city11}, open('tweetFrankfurt.json', 'w', encoding='utf-8'))
city12 = extractCity("53.575323,10.01534,100km")  # Hamburg
json.dump({'tweets': city12}, open('tweetHamburg.json', 'w', encoding='utf-8'))

clearMem()

city7 = extractCity("48.15,11.583333,100km")  # Munich
json.dump({'tweets': city7}, open('tweetMunich.json', 'w', encoding='utf-8'))
city8 = extractCity("47.5,19.083333,100km")  # Budapest
json.dump({'tweets': city8}, open('tweetBudapest.json', 'w', encoding='utf-8'))
city9 = extractCity("52.25,21.0,100km")  # Warsaw
json.dump({'tweets': city9}, open('tweetWarsaw.json', 'w', encoding='utf-8'))

clearMem()

city10 = extractCity("50.433333,30.516667,100km")  # Kiev
json.dump({'tweets': city10}, open('tweetKiev.json', 'w', encoding='utf-8'))
city11 = extractCity("44.433333,26.1,100km")  # Bucharest
json.dump({'tweets': city11}, open('tweetBucharest.json', 'w', encoding='utf-8'))
city12 = extractCity("60.175556,24.934167,100km")  # Helsinki
json.dump({'tweets': city12}, open('tweetHelsinki.json', 'w', encoding='utf-8'))
print("Rest of Europe Done.........!!")
###############################################################################
# ASIA
###############################################################################
clearMem()
city7 = extractCity("24.9056,67.0822,200km")  # Karachi
json.dump({'tweets': city7}, open('tweetKarachi.json', 'w', encoding='utf-8'))
city8 = extractCity("33.69,73.0551,200km")  # Islamabad
json.dump({'tweets': city8}, open('tweetIslamabad.json', 'w', encoding='utf-8'))
city9 = extractCity("28.651952,77.231495,200km")  # Delhi
json.dump({'tweets': city9}, open('tweetDelhi.json', 'w', encoding='utf-8'))

clearMem()

city10 = extractCity("18.987807,72.836447,200km")  # Bumbai
json.dump({'tweets': city10}, open('tweetBumbai.json', 'w', encoding='utf-8'))
city11 = extractCity("39.928819,116.388869,200km")  # Beijing
json.dump({'tweets': city11}, open('tweetBeijing.json', 'w', encoding='utf-8'))
city12 = extractCity("30.583333,114.266667,200km")  # Wuhan
json.dump({'tweets': city12}, open('tweetWuhan.json', 'w', encoding='utf-8'))
print("Asia Done.........!!")
###############################################################################
# Mics
###############################################################################
clearMem()
city7 = extractCity("30.07708,31.285909,200km")  # Cairo
json.dump({'tweets': city7}, open('tweetCairo.json', 'w', encoding='utf-8'))
city8 = extractCity("12.002381,8.51316,200km")  # Kano
json.dump({'tweets': city8}, open('tweetKano.json', 'w', encoding='utf-8'))
city9 = extractCity("35.705,51.4216,200km")  # Tehran
json.dump({'tweets': city9}, open('tweetTehran.json', 'w', encoding='utf-8'))

clearMem()

city10 = extractCity("-33.861481,151.205475,200km")  # Sydney
json.dump({'tweets': city10}, open('tweeSydney.json', 'w', encoding='utf-8'))
city11 = extractCity("-31.95224,115.861397,200km")  # Perth
json.dump({'tweets': city11}, open('tweetPerth.json', 'w', encoding='utf-8'))
city12 = extractCity("-36.866667,174.766667,200km")  # Auckland
json.dump({'tweets': city12}, open('tweetAuckland.json', 'w', encoding='utf-8'))
print("Mics Done.........!!")
###############################################################################
