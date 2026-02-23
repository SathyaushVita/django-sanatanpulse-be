from rest_framework import serializers
from ..models import MovieHeader

class MovieHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieHeader
        fields = '__all__'
