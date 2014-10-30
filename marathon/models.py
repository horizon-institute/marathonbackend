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
    url = models.CharField(max_length=300, default="", db_index=True, blank=True)
    lowres_video_url = models.CharField(max_length=300, default="", db_index=True, blank=True)
    online = models.BooleanField(db_index=True, default=False)
    public = models.BooleanField(db_index=True, default=False)
    thumbnail = models.CharField(max_length=300, default="")
    server_last_modified = models.DateTimeField(db_index=True, null=True, blank=True, default=None)
    
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
    content_type = models.CharField(db_index=True, max_length=15, choices=CONTENT_TYPE_CHOICES)
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

# NEW MODELS FOR SEARCH INTERFACE

class RacePoint(models.Model):
    event = models.ForeignKey(Event, db_index=True, null=False, blank=False)
    latitude = models.FloatField(null=False, blank=False, db_index=True)
    longitude = models.FloatField(null=False, blank=False, db_index=True)
    distance = models.IntegerField(null=False, blank=False, db_index=True)

    def __unicode__(self):
        return "%dm"%self.distance

class ModelDistance(models.Model):
    reference_point = models.ForeignKey(RacePoint, db_index=True, null=False, blank=False)
    accuracy = models.FloatField(null=False, blank=False, db_index=True)
    
    class Meta:
        abstract = True

class VideoDistance(ModelDistance):
    video = models.ForeignKey(Video, db_index=True, null=False, blank=False)

    def __unicode__(self):
        return u"%s at %s"%(self.video, self.reference_point.distance)

class LocationName(models.Model):
    name = models.CharField(max_length=200, db_index=True, null=False, blank=False)
    type = models.CharField(max_length=50, db_index=True, null=False, blank=False, default="Unknown")
    
    def __unicode__(self):
        return u"%s (%s)"%(self.name, self.type)

class LocationDistance(ModelDistance):
    location_name = models.ForeignKey(LocationName, related_name="points", db_index=True, null=False, blank=False)
    
    def __unicode__(self):
        return u"%s at %s"%(self.location_name, self.reference_point)

class RunningClub(models.Model):
    name = models.CharField(max_length=200, db_index=True, null=False, blank=False)
    
    def __unicode__(self):
        return self.name

class RaceResult(models.Model):
    event = models.ForeignKey(Event, db_index=True, null=False, blank=False)
    runner_number = models.IntegerField(db_index=True, null=False, blank=False)
    name = models.CharField(max_length=200, db_index=True, null=True, blank=True)
    finishing_time = models.IntegerField(db_index=True, null=False, blank=False)
    club = models.ForeignKey(RunningClub, related_name="runners", db_index=True, null=True)
    
    def __unicode__(self):
        return u"%s (#%d)"%(self.name, self.runner_number)
 
class SearchIndex(models.Model):
    
    INDEX_TYPES = (
                   ("LocationName","Location name"),
                   ("RunnerNumber","Runner"),
                   ("RunningClub","Running club"),
                   ("AtMinute","Time"),
                   ("AllVideos","All videos"),
                   ("AllTags","All tags")
                   )
    
    RESULT_TYPES = {
            "LocationName": "Video",
            "RunnerNumber": "RunnerTag",
            "RunningClub": "RunnerTag",
            "AtMinute": "RunnerTag",
            "AtKilometre": "Video",
            "AtMile": "Video",
            "AllVideos": "Video",
            "AllTags": "RunnerTag"
                    }
    
    KILOMETRE = 1000.
    
    MILE = 1609.344
    
    text = models.CharField(max_length=300, db_index=True, null=False, blank=False)
    type = models.CharField(max_length=50, db_index=True, null=False, blank=False)
    reference_index = models.IntegerField(db_index=True, null=False, blank=False)
    result_count = models.IntegerField(db_index=True)
    event = models.ForeignKey(Event, db_index=True, null=False, blank=False)
    
    def __unicode__(self):
        return '"%s" (%d %s)'%(self.text, self.result_count, self.result_type)
    
    def calculate_count(self):
        self.result_count = self.query_set.count()
    
    def ordinal(self, n):
        return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))
    
    @property
    def result_type(self):
        return self.RESULT_TYPES[self.type]
    
    @property
    def query_set(self):
        return getattr(self,"query_set_%s"%self.type,Video.objects.none())
    
    def get_query_set_between_distances(self, distance):
        return Video.objects
    
    @property
    def query_set_LocationName(self):
        refpoints = self.reference_object.points.all()
        return Video.objects.filter(
                online = True,
                event = self.event,
                videodistance__reference_point__in = refpoints,
                ).distinct()
    
    @property
    def query_set_RunnerNumber(self):
        return RunnerTag.objects.filter(
                            video__event = self.event,
                            video__online = True,
                            runner_number = self.reference_index
                                        )
    
    @property
    def query_set_RunningClub(self):
        rnos = RaceResult.objects.filter(
                              club = self.reference_index,
                              event = self.event,
                              ).values("runner_number")
        return RunnerTag.objects.filter(
                            video__event = self.event,
                            video__online = True,
                            runner_number__in=rnos
                            )
    
    @property
    def query_set_AtMinute(self):
        return RunnerTag.objects.filter(
                        video__event = self.event,
                        video__online = True,
                        time__gte = self.reference_object,
                        time__lt = (self.reference_object + datetime.timedelta(0,60))
                                        )
    
    def get_query_set_at_distance(self, distance_multiplier):
        return Video.objects.filter(
                        event = self.event,
                        online = True,
                        videodistance__reference_point__distance__gte=(self.reference_index-1)*distance_multiplier,
                        videodistance__reference_point__distance__lte=self.reference_index*distance_multiplier,
                                        )
    
    @property
    def query_set_AtKilometre(self):
        return self.get_query_set_at_distance(self.KILOMETRE)
    
    @property
    def query_set_AtMile(self):
        return self.get_query_set_at_distance(self.MILE)
    
    @property
    def query_set_AllVideos(self):
        return Video.objects.filter(
                            event=self.event,
                            online=True)
    
    @property
    def query_set_AllTags(self):
        return RunnerTag.objects.filter(video__event=self.event, video__online=True)
    
    
    @property
    def reference_object(self):
        return getattr(self,"reference_object_%s"%self.type,None)
    
    @property
    def reference_object_LocationName(self):
        return LocationName.objects.get(id=self.reference_index)
    
    @reference_object_LocationName.setter
    def reference_object_LocationName(self, value):
        self.type = "LocationName"
        self.text = unicode(value)
        self.reference_index = value.id
        self.calculate_count()
    
    @property
    def reference_object_RunnerNumber(self):
        return RaceResult.objects.get(
                                    event=self.event,
                                    runner_number=self.reference_index,
                                    )
    
    @reference_object_RunnerNumber.setter
    def reference_object_RunnerNumber(self, value):
        self.type = "RunnerNumber"
        self.text = unicode(value)
        self.reference_index = value.runner_number
        self.calculate_count()
    
    @property
    def reference_object_RunningClub(self):
        return RunningClub.objects.get(id=self.reference_index)
    
    @reference_object_RunningClub.setter
    def reference_object_RunningClub(self, value):
        self.type = "RunningClub"
        self.text = value.name
        self.reference_index = value.id
        self.calculate_count()
    
    
    @property
    def reference_object_AtMinute(self):
        return datetime.datetime.fromtimestamp(self.reference_index)
    
    @reference_object_AtMinute.setter
    def reference_object_AtMinute(self, value):
        self.type = "AtMinute"
        self.text = "Runners tagged at %s"%(value.strftime("%H:%M"))
        self.reference_index = int(value.strftime("%s"))
        self.calculate_count()
    
    @property
    def reference_object_AtKilometre(self):
        return self.reference_index
    
    @reference_object_AtKilometre.setter
    def reference_object_AtKilometre(self, value):
        self.type = "AtKilometre"
        self.text = "Videos at %s kilometre"%(self.ordinal(value))
        self.reference_index = value
        self.calculate_count()
    
    @property
    def reference_object_AtMile(self):
        return self.reference_index
    
    @reference_object_AtMile.setter
    def reference_object_AtMile(self, value):
        self.type = "AtKilometre"
        self.text = "Videos at %s mile"%(self.ordinal(value))
        self.reference_index = value
        self.calculate_count()
    
    @property
    def reference_object_AllVideos(self):
        return None
    
    @reference_object_AllVideos.setter
    def reference_object_AllVideos(self, value):
        self.type = "AllVideos"
        self.text = "All videos in event"
        self.reference_index = -1
        self.calculate_count()
        
    @property
    def reference_object_AllTags(self):
        return None
    
    @reference_object_AllTags.setter
    def reference_object_AllTags(self, value):
        self.type = "AllTags"
        self.text = "All tags in event"
        self.reference_index = -1
        self.calculate_count()
    