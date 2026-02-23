from rest_framework import viewsets
from rest_framework.response import Response
from ..models import MovieGeners
from ..serializers import MovieGenersSerializer

class MovieGenersViewSet(viewsets.ModelViewSet):
    queryset = MovieGeners.objects.all()
    serializer_class = MovieGenersSerializer

    def list(self, request, *args, **kwargs):
        filters = {}

        for key, value in request.query_params.items():
            filters[key] = value

        queryset = MovieGeners.objects.filter(**filters).order_by("-_id")

        serializer = self.serializer_class(queryset, many=True)

        return Response({
            "message": "success",
            "result": serializer.data
        })
