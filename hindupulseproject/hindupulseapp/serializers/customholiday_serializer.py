from rest_framework import serializers
from ..models import FixedHoliday

class FixedHolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedHoliday
        fields = '__all__'