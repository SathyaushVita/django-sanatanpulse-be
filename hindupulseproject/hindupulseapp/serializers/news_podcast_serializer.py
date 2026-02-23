from rest_framework import serializers
from ..models import NewsPodcast
from ..utils import image_path_to_binary1


class NewsPodcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPodcast
        fields = "__all__"





class NewsPodcastSerializer1(serializers.ModelSerializer):
    image_location = serializers.SerializerMethodField()

    def get_image_location(self, instance):
        filename = instance.image_location
        if filename:
            format = image_path_to_binary1(filename)
            return format
        return None


    
    class Meta:
        model = NewsPodcast
        fields = "__all__"








# from rest_framework import serializers
# from ..models import NewsPodcast
# from ..utils import image_path_to_binary1,video_path_to_binary


# class NewsPodcastSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = NewsPodcast
#         fields = "__all__"


# class NewsPodcastSerializer1(serializers.ModelSerializer):
#     image_location = serializers.SerializerMethodField()
#     video_location = serializers.SerializerMethodField()

#     def get_image_location(self, instance):
#         if instance.image_location:
#             return image_path_to_binary1(instance.image_location)
#         return None

#     def get_video_location(self, instance):
#         if instance.video_location:
#             return video_path_to_binary(instance.video_location)
#         return None

#     class Meta:
#         model = NewsPodcast
#         fields = "__all__"
