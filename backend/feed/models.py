from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
import uuid
from mutagen.mp4 import MP4,MP4StreamInfoError
from .helper import get_timer

#This needs to be shareable
class Mumble(models.Model):
    parent =models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    #For re-mumble (Share) functionality
    remumble = models.ForeignKey("self", on_delete=models.CASCADE, related_name='remumbles', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #content is allowed to be plan for remumbles
    content = RichTextField(null=True, blank=True)
    vote_rank = models.IntegerField(blank=True, null=True, default=0)
    comment_count = models.IntegerField(blank=True, null=True, default=0)
    share_count = models.IntegerField(blank=True, null=True, default=0)
    created = models.DateTimeField(auto_now_add=True)
    votes = models.ManyToManyField(User, related_name='mumble_user', blank=True, through='MumbleVote')
    id = models.UUIDField(default=uuid.uuid4,  unique=True, primary_key=True, editable=False)
    class Meta:
        ordering = ['-created']

    def __str__(self):
        try:
            content = self.content[0:80]
        except Exception:
            content = 'Remumbled: ' + str(self.remumble.content[0:80])
        return content

    @property
    def shares(self):
        queryset = self.remumbles.all()
        return queryset

    @property
    def comments(self):
        #Still need a way to get all sub elemsnts
        queryset = self.mumble_set.all()
        return queryset

class MumbleVote(models.Model):
    
    CHOICES = (
        ('upvote', 'upvote'),
        ('downvote', 'downvote'),
        )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    mumble = models.ForeignKey(Mumble, on_delete=models.CASCADE, null=True, blank=True)
    value = models.CharField(max_length=20, choices=CHOICES)
    id = models.UUIDField(default=uuid.uuid4,  unique=True, primary_key=True, editable=False)

    def __str__(self):
        return str(self.user) + ' ' +  str(self.value)  + '"' + str(self.mumble) + '"'


class Media(models.Model):
    mumble=models.ForeignKey(Mumble,null=False,blank=False,on_delete=models.CASCADE)
    title=models.CharField(max_length=225)
    file=models.FileField(upload_to='Mumblemedia')   #validators=[validate_video],
    length=models.DecimalField(max_digits=100,decimal_places=2)

    def get_video_length(self):
        try:
            video=MP4(self.file)
            return video.info.length
            
        except MP4StreamInfoError:
            return 0.0

    def get_video_length_time(self):
        return get_timer(self.length)
    
    def get_absolute_url(self):
        return self.file.url