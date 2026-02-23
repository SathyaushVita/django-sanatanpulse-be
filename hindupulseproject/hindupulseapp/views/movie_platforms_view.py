from rest_framework import viewsets
from rest_framework.response import Response
from ..models import MoviePlatforms
from ..serializers import MoviePlatformsSerializer

class MoviePlatformsViewSet(viewsets.ModelViewSet):
    queryset = MoviePlatforms.objects.all()
    serializer_class = MoviePlatformsSerializer

    def list(self, request, *args, **kwargs):
        filter_kwargs = {}

        # Add all query params directly to filter
        for key, value in request.query_params.items():
            filter_kwargs[key] = value

        queryset = MoviePlatforms.objects.filter(**filter_kwargs).order_by("-_id")

        serializer = self.serializer_class(queryset, many=True)
        return Response({
            "message": "success",
            "result": serializer.data
        })
