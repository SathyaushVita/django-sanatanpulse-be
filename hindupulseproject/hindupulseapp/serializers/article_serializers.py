from rest_framework import serializers
from ..models import ArticleModel,Register,ArticleProfile,ArticleCategory
from .article_category_serializers import ArticleCategorySerializer1
from ..utils import image_path_to_binary,image_path_to_binary1

from django.core.validators import RegexValidator
from django import forms
import json
from django.conf import settings


import json
import os
from azure.storage.blob import BlobServiceClient
from io import BytesIO



class ArticleSerializer(serializers.ModelSerializer):

    image_location = serializers.ListField(child=serializers.CharField(), required=False)


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Fields to check for empty or null values
        fields_to_check = ['_id', 'headline','desc','short_description' ,'status', 'location', 'category_id',  'image_location', 'audio_location','language', 'user','article_user','date']
        for field in fields_to_check:
            if representation.get(field) in [None, '', 'null', '-', '[]']:
                representation[field] = "null"
        return representation

    
    date = forms.CharField(
        max_length=4,
        validators=[RegexValidator(regex=r'^\d{4}$', message='Enter a valid year.')],
        help_text='Enter the year in YYYY format.'
    )
    class Meta:
        model = ArticleModel
        fields = ['_id', 'headline',  'desc', 'short_description','status', 'location', 'category_id',  'image_location','audio_location', 'language', 'user','article_user','date']


class ArticleSerializer2(serializers.ModelSerializer):

    class Meta:
        model = ArticleModel
        fields = '__all__'


class ArticleSerializer1(serializers.ModelSerializer):
    # pdf_location= serializers.SerializerMethodField()
    audio_location = serializers.SerializerMethodField()  # Add audio location
    user = serializers.SerializerMethodField(read_only=True)
    image_location = serializers.SerializerMethodField()
    article_user = serializers.SerializerMethodField(read_only=True)
    category_id=serializers.SerializerMethodField(read_only=True)
   
    def get_audio_location(self, instance):
        filename = instance.audio_location  # Handle audio similarly
        if filename:
            return image_path_to_binary(filename)
        return []
    def get_image_location(self, instance):
        filenames = instance.image_location
        if filenames:
            filenames = filenames[0]
            print("22222222222222222222", filenames)
            if filenames:
                format = image_path_to_binary1(filenames)
                return format
        return []

    def get_article_user(self, instance):
        try:
            article_user = instance.article_user
            if article_user:
                profile_pic_path = article_user.profile_pic
                if profile_pic_path:
                    base64_profile_pic = image_path_to_binary(profile_pic_path)
                    return {
                        "name": article_user.name,
                        "id": article_user.id,
                        "profile_pic": base64_profile_pic if base64_profile_pic else None,
                        "desc":article_user.desc,
                    }
                else:
                    return {
                        "name": article_user.name,
                        "id": article_user.id,
                        "profile_pic": None,
                        "desc":article_user.desc,
                    }
            return None
        except ArticleProfile.DoesNotExist:
            return None
    def get_category_id(self, instance):
        try:
            category_id = instance.category_id
            if category_id:
                profile_pic_path = category_id.profile_pic
                if profile_pic_path:
                    base64_profile_pic = image_path_to_binary(profile_pic_path)
                    return {
                        "name": category_id.name,
                        "id": category_id._id,
                        "profile_pic": base64_profile_pic if base64_profile_pic else None,
                    }
                else:
                    return {
                        "name": category_id.name,
                        "id": category_id.id,
                        "profile_pic": None,
                    }
            return None
        except ArticleCategory.DoesNotExist:
            return None


    def get_user(self, instance):
        try:
            user = instance.user
            if user:
                profile_pic_path = user.profile_pic
                if profile_pic_path:
                    base64_profile_pic = image_path_to_binary(profile_pic_path)
                    return {
                        "surname": user.surname,
                        "full_name": user.full_name,
                        "id": user.id,
                        "profile_pic": base64_profile_pic if base64_profile_pic else None,
                    }
                else:
                    return {
                        "surname": user.surname,
                        "full_name": user.full_name, 
                        "id": user.id,
                        "profile_pic": None,
                    }
            return None
        except Register.DoesNotExist:
            return None
  
    class Meta:
        model = ArticleModel
        fields = "__all__"





































































################################################ this is pdf_location article serializer ########################
# from rest_framework import serializers

# from ..models import ArticleModel,Register,ArticleProfile,ArticleCategory
# from .article_category_serializers import ArticleCategorySerializer1
# from ..utils import image_path_to_binary
# # from ..utils import image_path_to_binary,extract_pdf_content,download_pdf
# from django.core.validators import RegexValidator
# from django import forms
# import json
# from django.conf import settings
# import os,requests
# import tempfile


# import json
# import os
# from azure.storage.blob import BlobServiceClient
# from io import BytesIO



# class ArticleSerializer(serializers.ModelSerializer):
#     date = forms.CharField(
#         max_length=4,
#         validators=[RegexValidator(regex=r'^\d{4}$', message='Enter a valid year.')],
#         help_text='Enter the year in YYYY format.'
#     )
#     class Meta:
#         model = ArticleModel
#         fields = '__all__'


# class ArticleSerializer2(serializers.ModelSerializer):

#     class Meta:
#         model = ArticleModel
#         fields = '__all__'


# class ArticleSerializer1(serializers.ModelSerializer):
#     pdf_location= serializers.SerializerMethodField()
#     user = serializers.SerializerMethodField(read_only=True)
#     image_location= serializers.SerializerMethodField()
#     article_user = serializers.SerializerMethodField(read_only=True)
#     category_id=serializers.SerializerMethodField(read_only=True)
#     # pdf_contents = serializers.SerializerMethodField()
    

#     # def get_pdf_contents(self, instance):
#     #     # Initialize pdf_contents as a variable (string or None) instead of a list
#     #     pdf_content = None
#     #     print("22222222222222", pdf_content)

#     #     # Retrieve pdf_locations from the instance
#     #     pdf_location = instance.pdf_location
#     #     print("3333333333333", pdf_location)

#     #     # Check if pdf_locations is provided
#     #     if pdf_location:
#     #         print("55555555555555", pdf_location)
#     #         try:
#     #             # Attempt to load pdf_locations as JSON
#     #             pdf_paths = json.loads(pdf_location)
#     #             print("666666666666666", pdf_paths)
#     #         except (json.JSONDecodeError, TypeError):
#     #             # Handle invalid JSON format
#     #             pdf_paths = []
#     #             print("777777777777", pdf_paths)

#     #         # Process the first PDF path if available
#     #         if pdf_paths:
#     #             print("888888888888888888", pdf_paths)
#     #             first_path = pdf_paths[0]
#     #             print("99999999999999999", first_path)
#     #             # Extract content from the first PDF path
#     #             pdf_content = extract_pdf_content(first_path)
#     #             print("Extracted content:", pdf_content)

#     #     return pdf_content
    
    
#     # def get_pdf_contents(self, instance):
#     #     # Ensure Azure Blob Service Client is initialized
#     #     connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
#     #     blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
#     #     # Define your container name from settings
#     #     container_name = settings.AZURE_CONTAINER_NAME
#     #     container_client = blob_service_client.get_container_client(container_name)
    
#     #     pdf_location = instance.pdf_location
#     #     pdf_content = {"pdf_contents": []}
    
#     #     if pdf_location:
#     #         try:
#     #             # Retrieve the blob client from the container
#     #             blob_client = container_client.get_blob_client(pdf_location)
#     #             download_stream = blob_client.download_blob()
#     #             pdf_bytes = download_stream.readall()
    
#     #             # Write the PDF bytes to a temporary file
#     #             with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
#     #                 tmp_file.write(pdf_bytes)
#     #                 tmp_file_path = tmp_file.name
    
#     #             # Extract content from the PDF
#     #             pdf_content = extract_pdf_content(tmp_file_path)
#     #             print("Extracted content:", pdf_content)
    
#     #         except Exception as e:
#     #             print(f"Error reading PDF from Azure: {e}")
#     #             pdf_content = {"pdf_contents": None}
    
#     #     return {"pdf_contents111": pdf_content}

#     def get_article_user(self, instance):
#         try:
#             article_user = instance.article_user
#             if article_user:
#                 profile_pic_path = article_user.profile_pic
#                 if profile_pic_path:
#                     base64_profile_pic = image_path_to_binary(profile_pic_path)
#                     return {
#                         "name": article_user.name,
#                         "id": article_user.id,
#                         "profile_pic": base64_profile_pic if base64_profile_pic else None,
#                         "desc":article_user.desc,
#                     }
#                 else:
#                     return {
#                         "name": article_user.name,
#                         "id": article_user.id,
#                         "profile_pic": None,
#                         "desc":article_user.desc,
#                     }
#             return None
#         except ArticleProfile.DoesNotExist:
#             return None
#     def get_category_id(self, instance):
#         try:
#             category_id = instance.category_id
#             if category_id:
#                 profile_pic_path = category_id.profile_pic
#                 if profile_pic_path:
#                     base64_profile_pic = image_path_to_binary(profile_pic_path)
#                     return {
#                         "name": category_id.name,
#                         "id": category_id._id,
#                         "profile_pic": base64_profile_pic if base64_profile_pic else None,
#                     }
#                 else:
#                     return {
#                         "name": category_id.name,
#                         "id": category_id.id,
#                         "profile_pic": None,
#                     }
#             return None
#         except ArticleCategory.DoesNotExist:
#             return None


#     def get_user(self, instance):
#         try:
#             user = instance.user
#             if user:
#                 profile_pic_path = user.profile_pic
#                 if profile_pic_path:
#                     base64_profile_pic = image_path_to_binary(profile_pic_path)
#                     return {
#                         "surname": user.surname,
#                         "full_name": user.full_name,
#                         "id": user.id,
#                         "profile_pic": base64_profile_pic if base64_profile_pic else None,
#                     }
#                 else:
#                     return {
#                         "surname": user.surname,
#                         "full_name": user.full_name, 
#                         "id": user.id,
#                         "profile_pic": None,
#                     }
#             return None
#         except Register.DoesNotExist:
#             return None
#     def get_pdf_location(self, instance):
#         filename = instance.pdf_location  # Use the correct attribute name
#         if filename:
#             format = image_path_to_binary(filename)
#             return format
#         return []
#     def get_image_location(self, instance):
#         filename = instance.image_location  # Use the correct attribute name
#         if filename:
#             format = image_path_to_binary(filename)
#             return format
#         return []
#     class Meta:
#         model = ArticleModel
#         fields = "__all__"