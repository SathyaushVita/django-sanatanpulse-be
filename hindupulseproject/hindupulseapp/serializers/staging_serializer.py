





from rest_framework import serializers
from ..models import *
from ..utils import image_path_to_binary1,image_path_to_binary
from ..enums import LanguageEnum
from django.conf import settings




class StagingSerializer(serializers.ModelSerializer):
    image_location = serializers.ListField(child=serializers.CharField(), required=False)
    media = serializers.ListField(child=serializers.CharField(), required=False)
    language = serializers.PrimaryKeyRelatedField(
        source='language_id',   # maps to model field
        queryset=Language.objects.all()
    )
#     language = serializers.MultipleChoiceField(
#     choices=[(lang.value, lang.name) for lang in LanguageEnum],
#     required=False
# )

    # language = serializers.ChoiceField(choices=[(lang.value, lang.name) for lang in LanguageEnum])
    # print("wwwwwwwwwwwwwwwwwwwwwwwwwwwww",image_location)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Convert empty/null fields to "null"
        fields_to_check = ['_id', 'headline','desc','short_description','status','location',
                           'category_id','news_sub_category_id','image_location','audio_location',
                           'language','user','media','is_published','publish_at']
        for field in fields_to_check:
            if representation.get(field) in [None, '', 'null', '-', '[]']:
                representation[field] = "null"
        return representation
    
    class Meta:
        model = StagingModel
        fields = ['_id', 'headline','desc','short_description','status','location',
                  'category_id','news_sub_category_id','image_location','audio_location',
                  'language','user','media','is_published','publish_at']

  

class StagingSerializer1(serializers.ModelSerializer):
    image_location = serializers.SerializerMethodField()
    audio_location = serializers.SerializerMethodField()
    


    def get_image_location(self, instance):
        filenames = instance.image_location
        if filenames:
            filenames = filenames[0]
            print("22222222222222222222", filenames)
            if filenames:
                format = image_path_to_binary1(filenames)
                return format
        return []
    
    def get_audio_location(self, instance):
        filename = instance.audio_location  # Handle audio similarly
        if filename:
            return image_path_to_binary(filename)
        return []
    # def get_audio_location(self, instance):
    #     if instance.audio_location:
    #         return f"{settings.AZURE_BLOB_BASE_URL}/{instance.audio_location}"
    #     return None


    class Meta:
        model = StagingModel
        fields = "__all__"
       
