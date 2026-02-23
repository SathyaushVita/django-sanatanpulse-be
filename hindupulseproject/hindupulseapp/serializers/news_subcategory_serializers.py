from rest_framework import serializers
from ..models import NewsSubCategory 



class NewsSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsSubCategory
        fields = '__all__'

