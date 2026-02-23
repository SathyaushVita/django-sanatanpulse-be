from rest_framework import viewsets
from ..models import MovieHeader
from ..serializers import MovieHeaderSerializer

class MovieHeaderViewSet(viewsets.ModelViewSet):
    queryset = MovieHeader.objects.all()
    serializer_class = MovieHeaderSerializer
