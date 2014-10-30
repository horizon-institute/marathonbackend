from haystack import indexes
from marathon.models import Video

class VideoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    start_time = indexes.DateTimeField(model_attr="start_time")
    end_time = indexes.DateTimeField(model_attr="end_time")
    distances = indexes.MultiValueField()
    runners = indexes.MultiValueField()
    thumbnail = indexes.CharField(model_attr="thumbnail")
    
    def prepare_distances(self, obj):
        return [d.referencepoint.distance for d in obj.videodistance_set.all()]
    
    def prepare_runners(self, obj):
        return [d.label for d in obj.runnertags.all()]
    
    def get_model(self):
        return Video
    
    def index_queryset(self, using=None):
        return self.get_model().objects.filter(online=True)