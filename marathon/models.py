from django.db import models
from django.contrib.auth.models import User
import uuid
import datetime

# Create your models here.

class GUIDModel(models.Model):
    guid = models.CharField(max_length=100, unique=True)
    server_created_date = models.DateTimeField(db_index=True, null=False, blank=False, default=datetime.datetime.now)
    server_updated_date = models.DateTimeField(db_index=True, null=False, blank=False, default=datetime.datetime.now)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if not self.guid:
            self.guid = str(uuid.uuid4())
        self.server_updated_date = datetime.datetime.now()
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
    url = models.CharField(max_length=300, default="", db_index=True)
    online = models.BooleanField(db_index=True, default=False)
    public = models.BooleanField(db_index=True, default=False)
    thumbnail = models.CharField(max_length=300, default="")
    
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
    thumbnail = models.CharField(max_length=300, default="")
    
    @property
    def video_time(self):
        return (self.time - self.video.start_time).seconds
    
    @property
    def is_hot_tag(self):
        return (self.runner_number == -99)
    
    def __unicode__(self):
        return "Runner #%d tagged by %s at %s"%(self.runner_number, self.video.spectator.name, self.time)

class ContactRegistration(models.Model):
    email = models.EmailField(null=False, blank=False)
    registration_date = models.DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return self.email

class ContentFlag(models.Model):
    CONTENT_TYPE_CLASSES = { modelclass.__name__: modelclass for modelclass in [PositionUpdate, RunnerTag, Video]}
    CONTENT_TYPE_CHOICES = tuple([(k, k) for k in CONTENT_TYPE_CLASSES])
    user = models.ForeignKey(User, db_index=True, null=True, blank=True)
    content_type = models.CharField(max_length=15, choices=CONTENT_TYPE_CHOICES)
    content_id = models.IntegerField(db_index=True, null=False, blank=False)
    reason = models.TextField(null=True, blank=True)
    flag_date = models.DateTimeField(default=datetime.datetime.now)
    
    @property
    def content(self):
        try:
            return self.CONTENT_TYPE_CLASSES[self.content_type].objects.get(id=self.content_id)
        except:
            return None
        
    @property
    def video_content(self):
        return self.content if (self.content_type == "Video") else None
    
    @property
    def runnertag_content(self):
        return self.content if (self.content_type == "RunnerTag") else None
    
    @property
    def positionupdate_content(self):
        return self.content if (self.content_type == "PositionUpdate") else None
     
    def __unicode__(self):
        return "Flagged %s: id=%d"%(self.content_type,self.content_id)