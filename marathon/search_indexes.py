from haystack import indexes
from marathon.models import Video
from datetime import datetime

class VideoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    event = indexes.CharField(model_attr="event__name", faceted=True)
    time = indexes.MultiValueField(faceted=True)
    distance = indexes.MultiValueField(faceted=True)
    thumbnail = indexes.CharField(model_attr="thumbnail")
    
    def prepare_time(self, obj):
        res = []
        for d in obj.videodistance_set.all():
            k = int(d.reference_point.distance/1000)
            res.append("%d-%dm"%(1000*k,1000*(k+1)))
        return res
    
    def prepare_date(self, obj):
        DELTA = 1800
        res = []
        mint = DELTA*int(obj.start_time.strftime("%s")/DELTA)
        maxt = int(obj.end_time.strftime("%s"))
        for t in range(mint, maxt, DELTA):
            res.append("%s-%s"%(datetime.fromtimestamp(t).strftime("%H:%M"),datetime.fromtimestamp(t+DELTA).strftime("%H:%M")))
        return res
    
    def get_model(self):
        return Video
    
    def index_queryset(self, using=None):
        return self.get_model().objects.filter(online=True)