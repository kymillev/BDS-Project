import json
import os

from django.core.management.base import BaseCommand

from locations.models import Tweet, CountryInfo

tweets_created = 0
tweets_edited = 0


def add_tweet(tweet):
    global tweets_created
    global tweets_edited
    coords = tweet['coordinates']
    if isinstance(coords, dict):
        coords = coords['coordinates']
    uid = tweet['tweet_id']
    lang = tweet['lang']
    polarity = tweet['polarity']
    timestamp = tweet['timestamp']
    text = tweet['text']
    preprocessed_text = tweet['processed_text']
    if 'country' in tweet:
        country = tweet['country']
    else:
        country = ''
    try:
        # Overwrite previous text (it was already preprocessed when first added to database)
        # changed later to get original text
        t = Tweet.objects.get(uid=uid)
        if t.preprocessed_text == '':
            t.text = text
            t.preprocessed_text = preprocessed_text
            tweets_edited += 1
            t.save()
    except Tweet.DoesNotExist:
        t = Tweet.create(uid=uid, text=text, preprocessed_text=preprocessed_text, coords=coords,
                         timestamp=timestamp, lang=lang, polarity=polarity,country=country)
        tweets_created += 1
        t.save()


class Command(BaseCommand):

    def handle(self, *args, **options):
        global tweets_created
        global tweets_edited
        print('Starting import Tweets')

        dirname = 'assets/json/tweet_data'
        count = 0

        for file in os.listdir(dirname):
            if 'tweets_' in file:

                # Create country objects
                obj = json.load(open(os.path.join(dirname, file), 'r', encoding='utf-8'))
                name = obj['name']
                name_iso = obj['name_iso']
                geojson = obj['geojson']
                print('Current file for country:', name)
                try:
                    info = CountryInfo.objects.get(name_iso=name_iso)
                except CountryInfo.DoesNotExist:
                    info = CountryInfo.create(name=name, name_iso=name_iso, geojson=geojson)
                    info.save()

                tweets = obj['tweets']

                print(len(tweets), 'tweets found in file')
                for tweet in tweets:
                    count += 1
                    add_tweet(tweet)

            # We do this to get all the tweets that did not have country information of the countries we chose
            tweets2 = json.load(open('assets/json/tweets.json', 'r'))['tweets']
            for tweet in tweets2:
                count += 1
                add_tweet(tweet)

        print('TOTAL TWEETS:', count)
        print(tweets_created, 'tweets created', tweets_edited, 'tweets edited')
