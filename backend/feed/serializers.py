from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Mumble,Media
from users.serializers import UserProfileSerializer, UserSerializer

class MediaSerializer(serializers.ModelSerializer):
    length=serializers.CharField(source='get_video_length_time')
    file=serializers.CharField(source='get_absolute_url')
    class Meta:
        model=Media
        fields=[
            "title",
            "file",
            "length"
        ]

class MumbleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    original_mumble = serializers.SerializerMethodField(read_only=True)
    up_voters = serializers.SerializerMethodField(read_only=True)
    down_voters = serializers.SerializerMethodField(read_only=True)
    media=serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Mumble
        fields='__all__'
        # exclude=[]
        # field = ['id','comment_count','content','created','down_voters','original_mumble','parent','remumble','share_count','up_voters','user','vote_rank','votes','length','media',]

    
    def get_media(self,obj):
        medias=obj.media_set.all()
        serializer=MediaSerializer(medias,many=True)
        return serializer.data
    
    def get_user(self, obj):
        user = obj.user.userprofile
        serializer = UserProfileSerializer(user, many=False)
        return serializer.data


    def get_original_mumble(self, obj):
        original = obj.remumble
        if original != None:
            serializer = MumbleSerializer(original, many=False)
            return serializer.data
        else:
            return None

    def get_up_voters(self, obj):
        # Returns list of users that upvoted post
        voters = obj.votes.through.objects.filter(mumble=obj, value='upvote').values_list('user', flat=True)

        voter_objects = obj.votes.filter(id__in=voters)
        serializer = UserSerializer(voter_objects, many=True)
        return serializer.data

    def get_down_voters(self, obj):
        # Returns list of users that upvoted post
        voters = obj.votes.through.objects.filter(mumble=obj, value='downvote').values_list('user', flat=True)

        voter_objects = obj.votes.filter(id__in=voters)
        serializer = UserSerializer(voter_objects, many=True)
        return serializer.data


#video serializers


# class CourseSectionPaidSerializer(serializers.ModelSerializer):
#     episodes=VideoSerializer(many=True)
#     total_duduration=serializers.CharField(source='total_length')
#     class Meta:
#         model=Mumble
#         fields = '__all__'