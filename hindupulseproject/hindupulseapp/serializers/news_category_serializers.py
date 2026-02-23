
from rest_framework import serializers
from ..models import *
from ..utils import image_path_to_binary,image_path_to_binary1
from ..serializers import *
from django.utils.timesince import timesince

class NewsCategorySerializer3(serializers.ModelSerializer):
    image_location = serializers.SerializerMethodField()


    def get_image_location(self, instance):
        filenames = instance.image_location
        if filenames:
            filenames = filenames[0]
            print("22222222222222222222", filenames)
            if filenames:
                format = image_path_to_binary1(filenames)
                return format
        return []

    class Meta:
        model = NewsCategory
        fields = '__all__'

       
class NewsCategorySerializer(serializers.ModelSerializer):
    image_location = serializers.ListField(child=serializers.CharField(), required=False)
    media = serializers.ListField(child=serializers.CharField(), required=False)
    # print("qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq",image_location)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Fields to check for empty or null values
        fields_to_check = ['_id', 'headline','desc','short_description' ,'status', 'location', 'category_id', 'news_sub_category_id', 'image_location', 'audio_location','language', 'user','media']
        for field in fields_to_check:
            if representation.get(field) in [None, '', 'null', '-', '[]']:
                representation[field] = "null"
        return representation

    class Meta:
        model = NewsCategory
        fields = ['_id', 'headline',  'desc', 'short_description','status', 'location', 'category_id', 'news_sub_category_id', 'image_location','audio_location', 'language', 'user', 'media']
  



class NewsCategorySerializer1(serializers.ModelSerializer):
    category_id = serializers.SerializerMethodField()
    news_sub_category_id = serializers.SerializerMethodField()
    audio_location = serializers.SerializerMethodField()  # Add audio location
    # language_id = serializers.SerializerMethodField()
    image_location = serializers.SerializerMethodField()
    
    

    def get_category_id(self, instance):
        category = instance.category_id
        if category is not None:
            return {
            '_id': category._id,
            'name': category.name,
        }
        return None

    def get_news_sub_category_id(self, instance):
        sub_category = instance.news_sub_category_id
        if sub_category is not None:
            return {
                '_id': sub_category._id,
                'name': sub_category.name,
                'other_category': {
                    '_id': sub_category.other_category._id,
                    'name': sub_category.other_category.name,
                } if sub_category.other_category else None
            }
        return None

    # def get_language_id(self, instance):
    #     language = instance.language_id
    #     return {
    #         '_id': language._id,
    #         'name': language.name,
    #     }

   
    def get_image_location(self, instance):
        filenames = instance.image_location
        if filenames:
            filenames = filenames[0]
            print("33333333333", filenames)
            if filenames:
                format = image_path_to_binary1(filenames)
                return format
        return []
    
    def get_audio_location(self, instance):
        filename = instance.audio_location  # Handle audio similarly
        if filename:
            return image_path_to_binary(filename)
        return []


    class Meta:
        model = NewsCategory
        fields = "__all__"
       

class NewsCategorySerializer2(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ['_id','status'] 
 

# class NewsCategorySerializer2(serializers.ModelSerializer):
#     class Meta:
#         model = NewsCategory
#         # fields = ['_id','status'] 
#         fields = ['_id','image_location'] 
   
