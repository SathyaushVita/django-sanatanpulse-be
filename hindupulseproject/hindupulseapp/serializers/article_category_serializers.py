from rest_framework import serializers
from ..models import *
from ..utils import image_path_to_binary

class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = '__all__'
    
class ArticleCategorySerializer1(serializers.ModelSerializer):

    profile_pic = serializers.SerializerMethodField()
   
    def get_profile_pic(self, instance):
        filename = instance.profile_pic
        if filename:
            # Assuming image_path_to_binary is a utility function you have defined
            format = image_path_to_binary(filename)
            return format
        return []

    class Meta:
        model = ArticleCategory
        fields = '__all__'
