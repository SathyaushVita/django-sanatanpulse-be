from rest_framework import serializers
from ..models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


from rest_framework import serializers
from ..models import Category, NewsSubCategory

class NewsSubCategorySerializer1(serializers.ModelSerializer):
    class Meta:
        model = NewsSubCategory
        fields = ['_id', 'name']

class CategorySerializer1(serializers.ModelSerializer):
    subcategories = NewsSubCategorySerializer1(source='category_id1', many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['_id', 'name', 'priority_order', 'subcategories']