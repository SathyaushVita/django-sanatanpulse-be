from ..utils import image_path_to_binary1, video_path_to_binary
from rest_framework import serializers
from ..models import StagingMovieDetails
from ..utils import image_path_to_binary1

class StagingMovieDetailsSerializer(serializers.ModelSerializer):
    poster = serializers.SerializerMethodField()
    trailer = serializers.SerializerMethodField()
    platform = serializers.SerializerMethodField()

    def get_poster(self, instance):
        if instance.poster:
            return image_path_to_binary1(instance.poster)
        return []

    def get_trailer(self, instance):
        trailer = instance.trailer

        if not trailer:
            return None

        # If trailer is a list
        if isinstance(trailer, list):
            trailer = trailer[0]

        # If already full URL
        if trailer.startswith("http"):
            return trailer

        # Convert to full Azure URL
        return f"https://sathayushstorage.blob.core.windows.net/sathayush/{trailer}"


    def get_platform(self, instance):
        platform = instance.platform_id

        if not platform:
            return None

        return {
            "name": platform.name,
            "website": platform.website_links
        }

    class Meta:
        model = StagingMovieDetails
        fields = "__all__"
