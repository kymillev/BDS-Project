from django.urls import path

from locations import views

app_name = 'locations'

urlpatterns = [
    path('getSentimentScore/', views.get_sentiment_score, name='get_sentiment_score'),
    path('getTweetData/', views.get_tweet_data, name='get_tweet_data'),
    path('getTweets/', views.get_tweets, name='get_tweets'),
    path('getWordcloud/', views.get_wordcloud, name='get_wordcloud'),
    path('getFilterOptions/', views.get_filter_options, name='get_filter_options'),
    path('getGeojson/', views.get_geojson, name='get_geojson')
]
