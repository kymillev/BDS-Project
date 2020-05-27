import time
import re
import json

import numpy as np
from textblob import TextBlob

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max, Min

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.gis.db.models.functions import Distance as DistanceFunction

from .models import Tweet, CountryInfo



def get_sentiment_score(request):
    """
    :param request:
    :return: Sentiment and polarity score for given text
    """
    if not request.GET:
        return HttpResponse(status=400)
    else:
        sentiment_threshold = 0.2
        text = request.GET.get('text').lower()
        text = ' '.join(re.sub('(@[A-Za-z0-9]+)|([^0-9A-Za-z \\t]) |(\\w+://\\S+)', ' ', text).split())
        text = text.replace('#', ' ').replace('  ', ' ').strip()
        polarity = TextBlob(text).sentiment.polarity
        if polarity > sentiment_threshold:
            sentiment = 'Positive'
        elif polarity < -sentiment_threshold:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        return JsonResponse({'polarity': polarity, 'sentiment': sentiment})


def get_tweet_data(request):
    """
    Get data for a single tweet
    :param request:
    :return:
    """
    if not request.GET:
        return HttpResponse(status=400)
    else:
        id_ = request.GET.get('id')

        if id_ is None:
            return HttpResponse(status=400)

        try:
            tweet = Tweet.objects.get(uid=id_)
        except Tweet.DoesNotExist:
            return HttpResponse(status=400)

        res = {'text': tweet.text, 'polarity': tweet.polarity, 'sentiment': tweet.sentiment, 'lang': tweet.lang,
               'coords': tweet.get_coords(), 'timestamp': tweet.timestamp}

        return JsonResponse({'tweet': res})


def get_tweets(request):
    """
    Get all the coords + sentiments of tweets
    in range of the given latlng + distance
    :param request:
    :return:
    """
    t1 = time.time()
    default_limit = 200
    default_dist = 1
    if not request.GET:
        return HttpResponse(status=400)
    else:
        # If latlng is None, then we get all the data points
        latlng = request.GET.get('latlng')
        dist = request.GET.get('dist')
        limit = request.GET.get('limit')
        return_text = request.GET.get('return_text')
        lang = request.GET.get('lang')

        # Default distance of 1 km
        if dist is None:
            dist = default_dist
        # Default limit of 50 tweets
        if limit is None:
            limit = default_limit
        if return_text is None:
            return_text = False
        else:
            return_text = return_text.lower() == 'true' or str(return_text) == "1"
        if lang is None:
            lang = ''

        try:
            if latlng is not None:
                latlng = latlng.split(',')
                lat = float(latlng[0])
                lng = float(latlng[1])
            dist = float(dist)
            limit = int(limit)
            limit = min(max(limit, 1), default_limit)
            dist = max(dist, default_dist)

        except ValueError:
            return HttpResponse(status=400)

        if latlng is not None:
            # see: https://stackoverflow.com/questions/19703975/django-sort-by-distance
            # and: https://stackoverflow.com/questions/8464666/distance-between-2-points-in-postgis-in-srid-4326-in-metres
            degrees_distance = round((dist * 0.01), 2) + 0.01

            point = Point(lng, lat)
            tweets = Tweet.objects.filter(coords__dwithin=(point, degrees_distance)).annotate(
                distance=DistanceFunction('coords', point)).order_by('distance')
            if lang == '':
                tweets = tweets[:limit]

        else:
            tweets = Tweet.objects.filter(coords__isnull=False)

        if lang != '':
            tweets = tweets.filter(lang=lang)
            tweets = tweets[:limit]

        if return_text:
            res = [{'coords': t.get_coords(), 'tweet_id': t.uid, 'polarity': t.polarity, 'lang': t.lang,
                    'timestamp': t.timestamp.date(), 'country': t.country, 'text': t.text} for t in tweets]
        else:
            res = [{'coords': t.get_coords(), 'tweet_id': t.uid, 'polarity': t.polarity,
                    'lang': t.lang, 'timestamp': t.timestamp.date(), 'country': t.country} for t in tweets]

        print('Elapsed:', time.time() - t1)
        return JsonResponse({'tweets': res})


@csrf_exempt
def get_wordcloud(request):
    """
    Get the top words + their counts corresponding to the different sentiments (Positive,Neutral, and Negative)
    for the given IDs (this used in OnClick methods)
    :param request:
    :return:
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
        is_country = request.GET.get('country')
        tweet_ids = data['tweet_ids']
    except:
        return HttpResponse(status=400)
    t1 = time.time()
    limit = 100
    print('is country:', is_country)
    if is_country is not None:
        data = list(Tweet.objects.filter(uid__in=tweet_ids).values_list('preprocessed_text', 'polarity'))

        counts = [{}, {}, {}]
        amounts = [0, 0, 0]
        polarities = [0, 0, 0]

        # counting number of times each word comes up in list of words (in dictionary)
        for text, polarity in data:
            if polarity >= .2:
                idx = 1
            elif polarity <= -.2:
                idx = 2
            else:
                idx = -1
            amounts[0] += 1
            polarities[0] += polarity
            for word in text.split():
                if word in counts[0]:
                    counts[0][word] += 1
                else:
                    counts[0][word] = 1

            if idx > 0:
                amounts[idx] += 1
                polarities[idx] += polarity
                for word in text.split():
                    if word in counts[idx]:
                        counts[idx][word] += 1
                    else:
                        counts[idx][word] = 1

        polarities = [polarities[i] / amounts[i] for i in range(len(amounts)) if amounts[i] > 0]
        words = [[{'text': k, 'value': v} for k, v in sorted(c.items(), key=lambda x: x[1], reverse=True)[:limit]]
                 for c in counts]

        print('Elapsed:', time.time() - t1)
        return JsonResponse({'words': words, 'amounts': amounts, 'polarities': polarities})
    else:
        texts = list(Tweet.objects.filter(uid__in=tweet_ids).values_list('preprocessed_text', flat=True))

        counts = {}

        # counting number of times each word comes up in list of words (in dictionary)
        for text in texts:
            for word in text.split():
                if word in counts:
                    counts[word] += 1
                else:
                    counts[word] = 1

        words = [{'text': k, 'value': v} for k, v in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]]
        print('Elapsed:', time.time() - t1)
        return JsonResponse({'words': words})


def get_filter_options(request):
    min_date = Tweet.objects.all().aggregate(Min('timestamp'))['timestamp__min'].date()
    max_date = Tweet.objects.all().aggregate(Max('timestamp'))['timestamp__max'].date()
    lang_options = list(Tweet.objects.order_by().values_list('lang', flat=True).distinct())

    return JsonResponse(data={'min_date': min_date, 'max_date': max_date, 'lang_options': lang_options})


def get_geojson(request):
    """
    Returns geojson data for all countries in database
    :param request:
    :return:
    """
    infos = CountryInfo.objects.all()
    res = []
    for i in infos:
        res.append({'geojson': i.geojson, 'name': i.name, 'name_iso': i.name_iso})

    return JsonResponse(data={'geojson': res})

