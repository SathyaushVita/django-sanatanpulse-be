from rest_framework import serializers
from ..models import Media
from ..utils import image_path_to_binary,image_path_to_binary1


class MediaSerializer(serializers.ModelSerializer):
    image_location = serializers.ListField(child=serializers.CharField(), required=False)
    media = serializers.ListField(child=serializers.CharField(), required=False)
    class Meta:
        model = Media
        fields = '__all__'



class MediaSerializer1(serializers.ModelSerializer):
   

    image_location = serializers.SerializerMethodField()
    other_category = serializers.SerializerMethodField()

    def get_other_category(self, instance):
        category = instance.other_category

        if category :
            return {
                "_id": category._id,
                "name":category.name
            }
   
    # def get_image_location(self, instance):
    #     filenames = instance.image_location
    #     if filenames:
    #         filenames = filenames[0]
    #         print("33333333333", filenames)
    #         if filenames:
    #             format = image_path_to_binary1(filenames)
    #             return format
    #     return []
    def get_image_location(self, instance):
        filenames = instance.image_location  # Assuming this is a list of image file paths
        if filenames:
            images = []
            for filename in filenames:
                format = image_path_to_binary1(filename)  # Convert each image path to binary (base64)
                images.append(format)
            return images
        return []  # Return an empty list if no images are found
    
  


    class Meta:
        model = Media
        fields = "__all__"
       