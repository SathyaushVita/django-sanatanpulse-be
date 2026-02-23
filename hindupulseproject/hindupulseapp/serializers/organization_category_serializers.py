from rest_framework import serializers
from ..models import OrganizationCategory 



class OrganizationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationCategory
        fields = '__all__'

