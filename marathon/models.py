from django.db import models
from django.contrib.auth.models import User
import uuid
import datetime

# Create your models here.

class GUIDModel(models.Model):
    guid = models.CharField(max_length=100, unique=True)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if not self.guid:
            self.guid = str(uuid.uuid4())
        super(GUIDModel, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return getattr(self, "name", self.guid)

class Event(models.Model):
    date = models.DateField(db_index=True)
    public = models.BooleanField(db_index=True, default=False)
    is_current = models.BooleanField(db_index=True, default=False)
    name = models.CharField(max_length=200, db_index=True)
    
    def save(self, *args, **kwargs):
        if self.is_current:
            Event.objects.filter(is_current=True).exclude(id=self.id).update(is_current=False)
        super(Event, self).save(*args, **kwargs)
        
    def __unicode__(self):
        return self.name

class Spectator(GUIDModel):
    user = models.OneToOneField(User, null=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    
    def save(self, *args, **kwargs):
        if not self.name and self.user:
            self.name = self.user.username
        super(Spectator, self).save(*args, **kwargs)
    
    @property
    def last_position(self):
        try:
            return self.positionupdates.latest("time")
        except:
            return None

class PositionUpdate(GUIDModel):
    spectator = models.ForeignKey(Spectator, related_name="positionupdates", db_index=True, null=False, blank=False)
    time = models.DateTimeField(db_index=True, null=False, blank=False, default=datetime.datetime.now)
    latitude = models.FloatField(null=False, blank=False, db_index=True)
    longitude = models.FloatField(null=False, blank=False, db_index=True)
    accuracy = models.FloatField(null=False, blank=False, db_index=True)
    
    def __unicode__(self):
        return "%s at %s"%(self.spectator.name, self.time)

class Video(GUIDModel):
    event = models.ForeignKey(Event, related_name="videos", db_index=True, null=False, blank=False)
    spectator = models.ForeignKey(Spectator, related_name="videos", db_index=True, null=False, blank=False)
    start_time = models.DateTimeField(db_index=True, null=False, blank=False, default=datetime.datetime.now)
    duration = models.IntegerField(db_index=True, null=False, blank=False, default=0)
    url = models.CharField(max_length=300)
    online = models.BooleanField(db_index=True, default=False)
    public = models.BooleanField(db_index=True, default=False)
    
    @property
    def end_time(self):
        return self.start_time + datetime.timedelta(0, self.duration)
    
    def __unicode__(self):
        return "Video by %s at %s"%(self.spectator.name, self.start_time)

class RunnerTag(GUIDModel):
    video = models.ForeignKey(Video, related_name="runnertags", db_index=True, null=False, blank=False)
    runner_number = models.IntegerField(db_index=True, null=False, blank=False)
    time = models.DateTimeField(db_index=True, null=False, blank=False, default=datetime.datetime.now)
    latitude = models.FloatField(null=False, blank=False, db_index=True)
    longitude = models.FloatField(null=False, blank=False, db_index=True)
    accuracy = models.FloatField(null=False, blank=False, db_index=True)
    public = models.BooleanField(db_index=True, default=False)
    
    @property
    def video_time(self):
        return (self.time - self.video.start_time).seconds
    
    def __unicode__(self):
        return "Runner #%d tagged by %s at %s"%(self.runner_number, self.video.spectator.name, self.time)

    