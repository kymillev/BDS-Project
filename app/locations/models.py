import datetime
import pytz

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point, MultiPoint, Polygon
from django.contrib.postgres.fields import JSONField


class Tweet(models.Model):
    coords = models.PointField(null=True)
    text = models.CharField(max_length=1000)
    preprocessed_text = models.CharField(max_length=1000, default='')
    uid = models.CharField(max_length=200)
    timestamp = models.DateTimeField()
    polarity = models.FloatField()
    sentiment = models.CharField(max_length=50)
    lang = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=3, blank=True,default='')

    @classmethod
    def create(cls, uid, text, preprocessed_text, coords, timestamp, polarity, lang, country, sentiment_threshold=.2):
        """
        Constructor method
        """
        if polarity > sentiment_threshold:
            sentiment = 'Positive'
        elif polarity < -sentiment_threshold:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        if coords is not None:
            coords = Point(coords[0], coords[1])
        else:
            coords = None
        timestamp = datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)

        tweet = cls(uid=uid, text=text, preprocessed_text=preprocessed_text, coords=coords, timestamp=timestamp,
                    polarity=polarity, lang=lang, sentiment=sentiment, country=country)
        return tweet

    def __str__(self):
        return self.uid

    def get_coords(self):
        lnglat = self.coords.coords
        return {'lat': lnglat[1], 'lng': lnglat[0]}

    class Meta:
        verbose_name_plural = 'Tweets'
        ordering = ['uid']
        unique_together = ('uid',)


class CountryInfo(models.Model):
    geojson = JSONField()
    name = models.CharField(max_length=200)
    name_iso = models.CharField(max_length=3)

    @classmethod
    def create(cls, name, name_iso, geojson):
        """
        Constructor method
        """

        info = cls(name=name, name_iso=name_iso, geojson=geojson)
        return info

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = 'CountryInfos'
        ordering = ['name']
        unique_together = ('name_iso',)
