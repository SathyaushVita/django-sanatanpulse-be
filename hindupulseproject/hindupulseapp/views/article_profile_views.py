from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from ..models import ArticleProfile
from ..utils import save_image_to_azure,image_path_to_binary
from ..serializers import ArticleProfileSerializer,ArticleProfileSerializer1
from rest_framework import generics
from rest_framework.generics import GenericAPIView
import requests, os
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
import re
from rest_framework import viewsets
from ..serializers import MoreDetailsSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
import base64
from rest_framework import viewsets
from django.db.models import Case, When, Value
from django.db.models.functions import Cast
# from ..pagination import CustomPagination
from rest_framework.pagination import PageNumberPagination

sms_user = settings.SMS_USER
sms_password = settings.SMS_PASSWORD
sms_sender = settings.SMS_SENDER
sms_type = settings.SMS_TYPE
sms_template_id = settings.SMS_TEMPLATE_ID
RESEND_SMS = settings.RE_SMS_TEMPLATE_ID

class ArticlesCustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100

            
class GetArticleProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleProfileSerializer1
    queryset = ArticleProfile.objects.filter(status='SUCCESS').order_by("name")                                                                              
    paginator = ArticlesCustomPagination()
    

 

class GetArticleProfileName(APIView):
    def get(self, request):
        # Define the IDs that should appear at the top
        # priority_ids = ["56c3fb1f-487a-11ef-9995-00e04ca50182", "012964ee-487e-11ef-be7e-00e04ca50182"]  # Replace with your actual IDs
        
        # Get all profiles
        queryset = ArticleProfile.objects.filter(status='SUCCESS').order_by("name")
        
        # Sort queryset: profiles with priority IDs come first
        # queryset = sorted(queryset, key=lambda x: (x.id not in priority_ids, x.id))
        
        response_data = []

        # print(f"Total profiles found: {len(queryset)}")  # Debug statement
        
        for item in queryset:
            profile_pic_path = item.profile_pic
            base64_profile_pic = None
            if profile_pic_path:
                base64_profile_pic = image_path_to_binary(profile_pic_path)
            profile_data = {
                'id': item.id,
                'name': item.name,
                'profile_pic': base64_profile_pic  # Extract only the name field
            }
            
            print(f"Processing profile: {item.id}")  # Debug statement
            
            response_data.append(profile_data)
        
        print(f"Total profiles added to response: {len(response_data)}")  # Debug statement
        
        return Response(response_data, status=status.HTTP_200_OK)
    


class GetAllArticleProfileName(APIView):
    def get(self, request):
        # Define the IDs that should appear at the top
        # priority_ids = ["56c3fb1f-487a-11ef-9995-00e04ca50182", "012964ee-487e-11ef-be7e-00e04ca50182"]  # Replace with your actual IDs
        
        # Get all profiles
        queryset = ArticleProfile.objects.all().order_by("name")
        
        # Sort queryset: profiles with priority IDs come first
        # queryset = sorted(queryset, key=lambda x: (x.id not in priority_ids, x.id))
        
        response_data = []

        # print(f"Total profiles found: {len(queryset)}")  # Debug statement
        
        for item in queryset:
            profile_pic_path = item.profile_pic
            base64_profile_pic = None
            if profile_pic_path:
                base64_profile_pic = image_path_to_binary(profile_pic_path)
            profile_data = {
                'id': item.id,
                'name': item.name,
                'profile_pic': base64_profile_pic  # Extract only the name field
            }
            
            print(f"Processing profile: {item.id}")  # Debug statement
            
            response_data.append(profile_data)
        
        print(f"Total profiles added to response: {len(response_data)}")  # Debug statement
        
        return Response(response_data, status=status.HTTP_200_OK)

class GetArticleProfileNameById(APIView):
    def get(self, request,id):
        # Define the IDs that should appear at the top
        # priority_ids = ["56c3fb1f-487a-11ef-9995-00e04ca50182","012964ee-487e-11ef-be7e-00e04ca50182"]  # Replace with your actual IDs
        
        # Get all profiles
        queryset = ArticleProfile.objects.filter(id=id,status="SUCCESS")
        
        # Sort queryset: profiles with priority IDs come first
        # queryset = sorted(queryset, key=lambda x: (x.id not in priority_ids, x.id))
        
        response_data = []

        # print(f"Total profiles found: {len(queryset)}")  # Debug statement
        
        for item in queryset:
            profile_data = {
                'id':item.id,
                'name': item.name  # Extract only the name field
            }
            
            print(f"Processing profile: {item.id}")  # Debug statement
            
            response_data.append(profile_data)
        
        print(f"Total profiles added to response: {len(response_data)}")  # Debug statement
        
        return Response(response_data, status=status.HTTP_200_OK)

        

# class ArticleProfilePost(generics.GenericAPIView):
#     serializer_class = ArticleProfileSerializer
    
#     def send_email(self, email, subject, message):
#         from_email = settings.EMAIL_HOST_USER
#         recipient_list = [email]
#         try:
#             send_mail(subject, message, from_email, recipient_list)
#             print("Email sent successfully")
#         except Exception as e:
#             print(f"Failed to send email: {e}")

#     def post(self, request, *args, **kwargs):
#         # Retrieve profile_pic from request data
#         profile_pic = request.data.get('profile_pic')
#         print(profile_pic, "vfvfv")

#         # Instantiate the serializer with request data
#         serializer = self.get_serializer(data=request.data)
#         print("dddddddddd", serializer)
#         serializer.is_valid(raise_exception=True)
#         serializer.validated_data['is_member'] = "true"
#         serializer.save()

#         # If profile_pic is provided and not "null", save the image
#         if profile_pic and profile_pic != "null":
#             saved_location = save_image_to_azure(profile_pic, serializer.instance.id, serializer.instance.name, "author_profile")
#             if saved_location:
#                 serializer.instance.profile_pic = saved_location
#                 print(serializer.instance.profile_pic, "referg")
#                 serializer.instance.save()

#         # Send email with the required information
#         subject = 'Profile Updated'
#         message = 'REGISTRATION SUCCESSFUL, Now you are connected to our four websites. Thanks for being a part of Hindu Pulse!.'
#         recipient_email = 'sathayushtechsolutions@gmail.com'  
#         self.send_email(recipient_email, subject, message)

#         return Response({
#             "message": "Profile Added successfully",
#             "result": serializer.data
#         })

class ArticleProfilePost(generics.GenericAPIView):
    serializer_class = ArticleProfileSerializer
    
    def send_email(self, email, subject, message):
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        # # Print email content to the terminal
        # print("Sending email...")
        # print(f"From: {from_email}")
        # print(f"To: {recipient_list}")
        # print(f"Subject: {subject}")
        # print(f"Message:\n{message}")
        try:
            send_mail(subject, message, from_email, recipient_list)
            print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def post(self, request, *args, **kwargs):
        # Retrieve profile_pic from request data
        profile_pic = request.data.get('profile_pic')
        # print(profile_pic, "vfvfv")

        # Instantiate the serializer with request data
        serializer = self.get_serializer(data=request.data)
        print("dddddddddd", serializer)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['is_member'] = "true"
        serializer.save()

        # If profile_pic is provided and not "null", save the image
        if profile_pic and profile_pic != "null":
            saved_location = save_image_to_azure(profile_pic, serializer.instance.id, serializer.instance.name, "author_profile")
            if saved_location:
                serializer.instance.profile_pic = saved_location
                print(serializer.instance.profile_pic, "referg")
                serializer.instance.save()

        article_profile = serializer.instance
        article_details = f"Author Profile Details:\nID: {article_profile.id}\nName: {article_profile.name}"

        # Send email with the profile details
        subject = 'New Article Author Added'
        message = (
            "Article Author Profile Added successfully"
            "Thank you for being a part of Hindu Pulse!\n\n"
            f"{article_details}"
        )
        recipient_email = 'sathayushtechsolutions@gmail.com'  
        self.send_email(recipient_email, subject, message)

        return Response({
            "message": "Article Author Profile Added successfully",
            "result": serializer.data
        })



class UpdateArticleProfile(generics.GenericAPIView):
    serializer_class = ArticleProfileSerializer
    
    def send_email(self, email, subject, message):
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        try:
            send_mail(subject, message, from_email, recipient_list)
            print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def put(self, request, id):
        # Retrieve the instance
        instance = get_object_or_404(ArticleProfile, id=id)
        print("instance",instance)
        
        # Retrieve profile_pic from request data
        profile_pic = request.data.get('profile_pic')
        # print(profile_pic, "vfvfv")
        
        # Make a mutable copy of request.data and set profile_pic to "profile_pic"
        mutable_data = request.data.copy()
        mutable_data['profile_pic'] = "profile_pic"
        
        # Instantiate the serializer with the mutable copy of data
        serializer = self.get_serializer(instance, data=mutable_data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['is_member'] = "true"
        serializer.save()
        
        # If profile_pic is provided and not "null", save the image
        if profile_pic and profile_pic != "null":
            saved_location = save_image_to_azure(profile_pic, serializer.instance.id, serializer.instance.name,"author_profile")
            if saved_location:
                serializer.instance.profile_pic = saved_location
                print(serializer.instance.profile_pic, "referg")
                serializer.instance.save()
        
        article_profile = serializer.instance
        article_details = f"Author Profile Details:\nID: {article_profile.id}\nName: {article_profile.name}"

        # Send email with the profile details
        subject = 'New Article Author Added'
        message = (
            "Article Author Profile Added successfully"
            "Thank you for being a part of Hindu Pulse!\n\n"
            f"{article_details}"
        )
        recipient_email = 'sathayushtechsolutions@gmail.com'  
        self.send_email(recipient_email, subject, message)

        return Response({
            "message": "Article Author Profile Added successfully",
            "result": serializer.data
        })
