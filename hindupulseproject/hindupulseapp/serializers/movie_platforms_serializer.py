from rest_framework import serializers
from ..models import MoviePlatforms

class MoviePlatformsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoviePlatforms
        fields = '__all__'
