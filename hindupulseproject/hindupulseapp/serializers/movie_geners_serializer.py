from rest_framework import serializers
from ..models import MovieGeners

class MovieGenersSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieGeners
        fields = '__all__'
