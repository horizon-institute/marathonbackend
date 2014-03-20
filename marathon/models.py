from django.db import models
from django.contrib.auth.models import User
import uuid
import datetime

def make_converter(obj, baseattr, attrsuffix, factor):
    def _get(obj):
        return getattr(obj, baseattr, 0) / factor
    def _set(obj, value):
        setattr(obj, baseattr, value * factor)
    setattr(obj, "%s_%s"%(baseattr, attrsuffix), property(_get, _set))

def distanceDecorator(model):
    make_converter(model, "distance", "miles", 1609.344)
    make_converter(model, "distance", "km", 1000)
    return model

# Create your models here.

class GUIDModel(models.Model):
    guid = models.CharField(max_length=40, unique=True)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if not self.guid:
            self.guid = str(uuid.uuid4())
        super(GUIDModel, self).save(*args, **kwargs)

class Event(models.Model):
    date = models.DateField(db_index=True)
    public = models.BooleanField(db_index=True)
    name = models.CharField(max_length=200, db_index=True)

@distanceDecorator
class RaceType(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    distance = models.FloatField(db_index=True, null=False, blank=False)

class Race(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    start = models.DateTimeField(db_index=True)
    event = models.ForeignKey(Event, related_name="races", db_index=True)
    racetype = models.ForeignKey(RaceType, db_index=True)
    start_time = models.DateTimeField(db_index=True)
    
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = u'"%s" in "%s"'%(self.racetype.name,self.event.name)
        super(Race, self).save(*args, **kwargs)

class Finisher(models.Model):
    race = models.ForeignKey(Race, related_name="runners", db_index=True)
    bib_number = models.IntegerField(db_index=True)
    start_time = models.DateTimeField(db_index=True)
    finish_time = models.DateTimeField(db_index=True)
    
    def _calculate_times(self):
        if hasattr(self, "_chip_time") and hasattr(self, "_gun_time") and self.race and self.race.start_time:
            self.finish_time = self.race.start_time + datetime.timedelta(0, self._gun_time)
            self.start_time = self.finish_time - datetime.timedelta(0, self._chip_time)
            del self._gun_time
            del self._chip_time
    
    @property
    def chip_time(self):
        if (hasattr(self, "_chip_time")):
            return self._chip_time
        return (self.finish_time - self.start_time).seconds
    
    @chip_time.setter
    def chip_time(self, value):
        self._chip_time = value
        self._calculate_times()
    
    @property
    def gun_time(self):
        if (hasattr(self, "_gun_time")):
            return self._gun_time
        return (self.finish_time - self.race.start_time).seconds
    
    @gun_time.setter
    def gun_time(self, value):
        self._gun_time = value
        self._calculate_times()
    
    @property
    def average_speed(self):
        return float(self.race.racetype.distance) / self.chip_time
    
    def save(self, *args, **kwargs):
        if not (self.start_time and self.finish_time):
            self._calculate_times()
        super(Race, self).save(*args, **kwargs)
    
    class Meta:
        unique_together = ("race", "bib_number")

class Spectator(GUIDModel):
    # isn't useful in the second experimentation, but provides compatibility with 2013 data
    user = models.OneToOneField(User, null=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    
    def save(self, *args, **kwargs):
        if not self.name and self.user:
            self.name = self.user.username
        super(Spectator, self).save(*args, **kwargs)

@distanceDecorator
class Video(GUIDModel):
    event = models.ForeignKey(Event, related_name="videos", db_index=True, null=False, blank=False)
    spectator = models.ForeignKey(Spectator, related_name="videos", db_index=True, null=False, blank=False)
    start_time = models.DateTimeField(db_index=True, null=False, blank=False)
    duration = models.IntegerField(db_index=True, null=False, blank=False)
    distance = models.FloatField(db_index=True, null=False, blank=False)
    latitude = models.FloatField(null=False, blank=False)
    longitude = models.FloatField(null=False, blank=False)
    url = models.CharField(max_length=300)
    
    @property
    def end_time(self):
        return self.time + datetime.timedelta(0, self.duration)

@distanceDecorator
class Tag(GUIDModel):
    video = models.ForeignKey(Video, related_name="tags", db_index=True, null=False, blank=False)
    time = models.DateTimeField(db_index=True, null=False, blank=False)
    distance = models.FloatField(db_index=True, null=False, blank=False)
    latitude = models.FloatField(null=False, blank=False)
    longitude = models.FloatField(null=False, blank=False)
    runner_number = models.IntegerField(db_index=True, null=False, blank=False)
    finisher = models.ForeignKey(Finisher, related_name="tags", db_index=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.latitude and self.video:
            self.latitude = self.video.latitude
        if not self.longitude and self.video:
            self.longitude = self.video.longitude
        if not self.distance and self.video:
            self.distance = self.video.distance
        super(Tag, self).save(*args, **kwargs)