from rest_framework import viewsets
from ..models import FixedHoliday
from ..serializers import FixedHolidaySerializer

class FixedHolidayViewSet(viewsets.ModelViewSet):
   
    queryset = FixedHoliday.objects.all()
    serializer_class = FixedHolidaySerializer
