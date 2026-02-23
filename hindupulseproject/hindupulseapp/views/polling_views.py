from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Poll, PollResponse
from ..serializers import PollSerializer, PollResponseSerializer

from django.db.models import Count
from django.db import models
from django.db.models import Count, Q

class PollListCreateView(generics.ListCreateAPIView):
    queryset = Poll.objects.annotate(
        yes_count=Count('responses', filter=Q(responses__response='YES')),
        no_count=Count('responses', filter=Q(responses__response='NO'))
    )
    serializer_class = PollSerializer

from django.db import IntegrityError
# class PollResponseCreateView(generics.CreateAPIView):
#     serializer_class = PollResponseSerializer
#     permission_classes = [IsAuthenticated]  # Ensure only authenticated users can respond

#     def create(self, request, *args, **kwargs):
#         try:
#             # Validate and save the response
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save(user=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except IntegrityError:
#             return Response(
#                 {"error": "You have already responded to this poll."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )


class PollResponseCreateView(generics.CreateAPIView):
    serializer_class = PollResponseSerializer
    # permission_classes = [IsAuthenticated]  # Ensure only authenticated users can respond

    def create(self, request, *args, **kwargs):
        # Validate and save the response using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
