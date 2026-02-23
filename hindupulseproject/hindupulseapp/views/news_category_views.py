from rest_framework import viewsets
from ..models import NewsCategory,Category,Register
from ..enums.member_status_enum import MemberStatus
from ..serializers import *
from ..pagination.pagination import CustomPagination 
from ..utils import save_image_to_azure_v2,save_audio_to_azure
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status as http_status
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from rest_framework import status
from ..enums import EntityStatus
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from django.utils.timesince import timesince
from datetime import datetime, timedelta
from django.utils.timezone import make_aware,get_current_timezone
from django.utils.timezone import make_aware, is_naive, get_current_timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from pytz import timezone
from django.utils.timezone import make_aware, get_current_timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone
import re
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
import uuid



from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from ..models import StagingModel, NewsCategory
from ..serializers import StagingSerializer, NewsCategorySerializer3
from django.shortcuts import get_object_or_404



from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.permissions import IsAuthenticated

from django.http import HttpResponse

from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.utils import ImageReader
import requests
from ..utils import translate_text_sarvam,generate_speech_sarvam

# class NewsCategoryViewSet(viewsets.ModelViewSet):
#     queryset = NewsCategory.objects.filter(status='SUCCESS',is_published='PUBLISHED').order_by('-created_at')
#     # queryset = NewsCategory.objects.filter(status='SUCCESS',is_published='PUBLISHED').order_by('-created_at')
#     serializer_class = NewsCategorySerializer1
#     pagination_class = CustomPagination
#     newscategory = NewsCategory.objects.filter(status='SUCCESS',is_published='PUBLISHED')
# class NewsCategoryViewSet(viewsets.ModelViewSet):
#     queryset = NewsCategory.objects.filter(status='SUCCESS',publish_at__lte=timezone.now()).order_by('-publish_at')  # Order by publish_at time
#     serializer_class = NewsCategorySerializer1
#     pagination_class = CustomPagination
class NewsCategoryViewSet(viewsets.ModelViewSet):
    queryset = NewsCategory.objects.filter(
        status='SUCCESS',
        is_published='PUBLISHED'
    ).order_by('-created_at')

    serializer_class = NewsCategorySerializer1
    pagination_class = CustomPagination

    # ---------------------------------------
    # LIST API  (GET ALL)
    # ---------------------------------------
    def list(self, request, *args, **kwargs):

        language_id = request.query_params.get("language")
        target_lang = LANGUAGE_UUID_TO_CODE.get(language_id, "en")

        queryset = self.filter_queryset(self.get_queryset())
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        results = []

        for obj in page:
            data = self.serializer_class(obj).data

            headline = data.get("headline") or ""
            short_description = data.get("short_description") or ""
            desc = data.get("desc") or ""

            # --------------------------
            # TRANSLATION
            # --------------------------
            if target_lang != "en":
                try:
                    headline = translate_text_sarvam(headline, target_lang)
                except:
                    pass

                try:
                    short_description = translate_text_sarvam(short_description, target_lang)
                except:
                    pass

                desc = self.translate_long_text(desc, target_lang)

            # --------------------------
            # AUDIO GENERATION
            # --------------------------
            audio_url = generate_speech_sarvam(desc or headline, target_lang)

            # --------------------------
            # UPDATE EACH ITEM
            # --------------------------
            data.update({
                "headline": headline,
                "short_description": short_description,
                "desc": desc,
                "audio_url": audio_url
            })

            results.append(data)

        return paginator.get_paginated_response(results)

    # ------------------------------------------
    # CHUNKED TRANSLATION
    # ------------------------------------------
    def translate_long_text(self, text, target_lang):
        max_len = 900
        final_txt = ""

        for i in range(0, len(text), max_len):
            chunk = text[i:i + max_len]
            try:
                translated = translate_text_sarvam(chunk, target_lang)
                final_txt += translated or chunk
            except:
                final_txt += chunk

        return final_txt


class AddNewsCategoryView(generics.GenericAPIView):
    serializer_class = NewsCategorySerializer
    permission_classes = []
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT']:
            return [IsAuthenticated()]
        return super().get_permissions()
    def is_email(self, username):
        return re.match(r"[^@]+@gmail\.com$", username)
    def send_email(self, email, subject, message):
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        try:
            send_mail(subject, message, from_email, recipient_list)
            print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {e}")
    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        try:
            user = Register.objects.get(id=user_id)
            if user.is_member != MemberStatus.true.value:
                return JsonResponse({"error": "User is not a member"}, status=400)
        except Register.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        audio_location = request.data.get('audio_location')  # New audio location
        image_location = request.data.get('image_location', [])
        if not isinstance(image_location, list):
            return JsonResponse({"error": "Image location must be a list"}, status=400)
        if len(image_location) > 3:
            return JsonResponse({"error": "You cannot upload more than three images"}, status=400)
        # Make a mutable copy of request.data
        mutable_data = request.data.copy()
        mutable_data['image_location'] = []
        mutable_data['audio_location'] = "null"  # Set audio initially to null
        # Instantiate the serializer with the mutable copy
        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        saved_image_paths = []
        for idx, image_data in enumerate(image_location):
            if image_data:
                saved_location = save_image_to_azure_v2(image_data, serializer.instance._id, 'news', f'image{idx + 1}')
                if saved_location:
                    saved_image_paths.append(saved_location)
        if saved_image_paths:
            serializer.instance.image_location = saved_image_paths
            serializer.instance.save()
        if audio_location and audio_location != "null":  # Handle audio upload
            saved_audio_location = save_audio_to_azure(audio_location, serializer.instance._id, serializer.instance.category_id.name, "news")
            if saved_audio_location:
                serializer.instance.audio_location = saved_audio_location
                serializer.instance.save()
        # Send email with the required information
        subject = ':loudspeaker: New News Added'
        details = "\n                ".join([f"{key}: {value}" for key, value in serializer.data.items()])
        message = f"""User Details:
                        User ID: {user_id}
                        First Name: {user.surname}
                        Last Name: {user.full_name}
                        Contact Number: {user.contact_number}
                    Details:
                        {details}
        """
        recipient_email = 'sathayushtechsolutions@gmail.com'  # replace with your email
        self.send_email(recipient_email, subject, message)
        return Response({
            "message": "success",
            "result": serializer.data
        })













class EditNews(generics.GenericAPIView):
    serializer_class = NewsCategorySerializer

    def is_email(self, username):
        return re.match(r"[^@]+@gmail\.com$", username)

    def send_email(self, email, subject, message):
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        try:
            send_mail(subject, message, from_email, recipient_list)
            print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def get_user_details(self, user_id):
        try:
            user = Register.objects.get(id=user_id)
            return {
                "user_id": user.id,
                "surname": user.surname,
                "full_name": user.full_name,
                "contact_number": user.contact_number,
            }
        except Register.DoesNotExist:
            return None

    def put(self, request, _id):
        user_id = request.data.get('user')
        if not user_id:
            return Response({"error": "User ID is required"}, status=400)
        
        user_details = self.get_user_details(user_id)
        if not user_details:
            return Response({"error": "User not found"}, status=404)

        # Retrieve the instance
        instance = get_object_or_404(NewsCategory, _id=_id)

        audio_location = request.data.get('audio_location')  # New audio location

        # Retrieve image_location from request data
        image_location = request.data.get('image_location', [])
        if not isinstance(image_location, list):
            return JsonResponse({"error": "Image location must be a list"}, status=400)
        if len(image_location) > 3:
            return JsonResponse({"error": "You cannot upload more than three images"}, status=400)

        # Make a mutable copy of request.data
        mutable_data = request.data.copy()
        mutable_data['image_location'] = instance.image_location  # Preserve existing image locations
        mutable_data['audio_location'] = "null"  # Set audio initially to null


        # Instantiate the serializer with the mutable copy and instance
        serializer = self.get_serializer(instance, data=mutable_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        saved_image_paths = []
        for idx, image_data in enumerate(image_location):
            if image_data and image_data != "null":
                saved_location = save_image_to_azure_v2(image_data, serializer.instance._id, 'news', f'image{idx + 1}')
                if saved_location:
                    saved_image_paths.append(saved_location)

        # Update the instance with new image locations if any images were saved
        if saved_image_paths:
            serializer.instance.image_location = saved_image_paths
            serializer.instance.save()

        if audio_location and audio_location != "null":  # Handle audio upload
            saved_audio_location = save_audio_to_azure(audio_location, serializer.instance._id, serializer.instance.category_id.name, "news")
            if saved_audio_location:
                serializer.instance.audio_location = saved_audio_location
                serializer.instance.save()

     
        # Send email with the required information
        subject = '📢 Edit News Added'
        message = f"""User Details:
        User ID: {user_details['user_id']}
        First Name: {user_details['surname']}
        Last Name: {user_details['full_name']}
        Contact Number: {user_details['contact_number']}
        Details: {serializer.data}
        """
        recipient_email = 'sathayushtechsolutions@gmail.com'  # replace with your email
        self.send_email(recipient_email, subject, message)

        return Response({
            "message": "success",
            "result": serializer.data
        })




class UpdateNews_Production(generics.GenericAPIView):
    serializer_class = NewsCategorySerializer

    # def is_email(self, username):
    #     return re.match(r"[^@]+@gmail\.com$", username)

    # def send_email(self, email, subject, message):
    #     from_email = settings.EMAIL_HOST_USER
    #     recipient_list = [email]
    #     try:
    #         send_mail(subject, message, from_email, recipient_list)
    #         print("Email sent successfully")
    #     except Exception as e:
    #         print(f"Failed to send email: {e}")

    # def get_user_details(self, user_id):
    #     try:
    #         user = Register.objects.get(id=user_id)
    #         return {
    #             "user_id": user.id,
    #             "surname": user.surname,
    #             "full_name": user.full_name,
    #             "contact_number": user.contact_number,
    #         }
    #     except Register.DoesNotExist:
    #         return None

    def put(self, request, _id):
        # user_id = request.data.get('user')
        # if not user_id:
        #     return Response({"error": "User ID is required"}, status=400)
        
        # user_details = self.get_user_details(user_id)
        # if not user_details:
        #     return Response({"error": "User not found"}, status=404)

        # Retrieve the instance
        instance = get_object_or_404(NewsCategory, _id=_id)
        instance.created_at = timezone.now()

        audio_location = request.data.get('audio_location')  # New audio location

        # Retrieve image_location from request data
        image_location = request.data.get('image_location', [])
        if not isinstance(image_location, list):
            return JsonResponse({"error": "Image location must be a list"}, status=400)
        if len(image_location) > 3:
            return JsonResponse({"error": "You cannot upload more than three images"}, status=400)

        # Make a mutable copy of request.data
        mutable_data = request.data.copy()
        mutable_data['image_location'] = instance.image_location  # Preserve existing image locations
        mutable_data['audio_location'] = "null"  # Set audio initially to null


        # Instantiate the serializer with the mutable copy and instance
        serializer = self.get_serializer(instance, data=mutable_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        saved_image_paths = []
        for idx, image_data in enumerate(image_location):
            if image_data and image_data != "null":
                saved_location = save_image_to_azure_v2(image_data, serializer.instance._id, 'news', f'image{idx + 1}')
                if saved_location:
                    saved_image_paths.append(saved_location)

        # Update the instance with new image locations if any images were saved
        if saved_image_paths:
            serializer.instance.image_location = saved_image_paths
            serializer.instance.save()

        if audio_location and audio_location != "null":  # Handle audio upload
            saved_audio_location = save_audio_to_azure(audio_location, serializer.instance._id, serializer.instance.category_id.name, "news")
            if saved_audio_location:
                serializer.instance.audio_location = saved_audio_location
                serializer.instance.save()

     
        # Send email with the required information
        # subject = '📢 Edit News Added'
        # message = f"""User Details:
        # User ID: {user_details['user_id']}
        # First Name: {user_details['surname']}
        # Last Name: {user_details['full_name']}
        # Contact Number: {user_details['contact_number']}
        # Details: {serializer.data}
        # """
        # recipient_email = 'sathayushtechsolutions@gmail.com'  # replace with your email
        # self.send_email(recipient_email, subject, message)

        return Response({
            "message": "success",
            "result": {
                "entered_data": request.data,  # Return exactly what was entered
                "saved_data": serializer.data,  # Return saved serializer data
            }
        })

    

    
class Production_Edit(generics.GenericAPIView):
    serializer_class = NewsCategorySerializer
    # permission_classes = []

    # def get_permissions(self):
    #     if self.request.method in ['POST', 'PUT']:
    #         return [IsAuthenticated()]
    #     return super().get_permissions()

    def put(self, request, _id):
        # Retrieve the instance
        instance = get_object_or_404(NewsCategory, _id=_id)

        # Retrieve image_location and audio_location from request data
        audio_location = request.data.get('audio_location')
        image_location = request.data.get('image_location', [])
        
        # Validate that image_location is a list
        if not isinstance(image_location, list):
            return JsonResponse({"error": "Image location must be a list"}, status=400)
        if len(image_location) > 3:
            return JsonResponse({"error": "You cannot upload more than three images"}, status=400)

        # Prepare mutable data for serializer
        mutable_data = request.data.copy()
        mutable_data['image_location'] = instance.image_location  # Preserve existing images
        mutable_data['audio_location'] = "null"  # Set audio to null initially

        # Create and validate serializer
        serializer = self.get_serializer(instance, data=mutable_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Process and save new images
        saved_image_paths = []
        for idx, image_data in enumerate(image_location):
            if image_data and image_data != "null":
                saved_location = save_image_to_azure_v2(image_data, serializer.instance._id, 'news', f'image{idx + 1}')
                if saved_location:
                    saved_image_paths.append(saved_location)

        # Update instance with new image locations if any were saved
        if saved_image_paths:
            serializer.instance.image_location = saved_image_paths
            serializer.instance.save()

        # Handle audio upload
        if audio_location and audio_location != "null":
            saved_audio_location = save_audio_to_azure(audio_location, serializer.instance._id, serializer.instance.category_id.name, "news")
            if saved_audio_location:
                serializer.instance.audio_location = saved_audio_location
                serializer.instance.save()

        # Return the response with the original data
        return Response({
            "message": "success",
            "result": {
                "entered_data": request.data,  # Return exactly what was entered
                "saved_data": serializer.data,  # Return saved serializer data
            }
        })
    
# class GetItemByfield_InputView(APIView):
#     serializer_class = NewsCategorySerializer1
#     pagination_class = CustomPagination

#     def get(self, request, *args, **kwargs):
#         queryset = NewsCategory.objects.filter(status='SUCCESS',is_published='PUBLISHED').order_by('-created_at')
#         # queryset = NewsCategory.objects.filter(status='SUCCESS',is_published='PUBLISHED').order_by('-created_at')
#         # queryset = NewsCategory.objects.filter(status='SUCCESS', publish_at__lte=timezone.now()).order_by('-publish_at')

#         category_id = request.query_params.get('category_id')
#         news_sub_category_id = request.query_params.get('news_sub_category_id')
#         created_at = request.query_params.get('created_at')
#         language = request.query_params.get('language')

#         # Filter by category_id if provided
#         if category_id:
#             queryset = queryset.filter(
#                 Q(category_id=category_id) | Q(news_sub_category_id=category_id)
#             )

#         # Filter by news_sub_category_id if provided
#         if news_sub_category_id:
#             queryset = queryset.filter(news_sub_category_id=news_sub_category_id)
#         if language:
#             queryset = queryset.filter(language=language)

#         if created_at:
#             try:
#                 if created_at.lower() == 'today':
#                     start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#                     end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
#                 elif created_at.lower() == 'yesterday':
#                     start_date = (timezone.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
#                     end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
#                 elif created_at.lower() in ['1 week ago', '2 weeks ago', '3 weeks ago', 'this month', 'last month',
#                                             '1 month ago', '2 months ago', '3 months ago', '4 months ago', '5 months ago']:
#                     # Handle specific date ranges
#                     start_date, end_date = self.get_date_range(created_at)
#                 else:
#                     # Handle specific date format YYYY-MM-DD
#                     start_date = timezone.make_aware(datetime.strptime(created_at, '%Y-%m-%d'), timezone.get_current_timezone())
#                     start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
#                     end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)

#                 # Check if start_date is older than 4 months from now
#                 if start_date < timezone.now() - timedelta(days=120):
#                     return Response({
#                         'message': 'No data available older than 4 months. All data has been cleared.',
#                         'status': 204  # Custom status code indicating no content
#                     }, status=status.HTTP_204_NO_CONTENT)

#             except ValueError:
#                 return Response({
#                     'message': 'Invalid date format',
#                     'status': 400
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             queryset = queryset.filter(created_at__range=(start_date, end_date))

#         # Pagination
#         paginator = CustomPagination()
#         paginated_queryset = paginator.paginate_queryset(queryset, request)
#         serializer = NewsCategorySerializer1(paginated_queryset, many=True)
#         return paginator.get_paginated_response(serializer.data)

#     def get_date_range(self, created_at):
#         """ Helper function to get date range based on relative date string """
#         if created_at.lower() == 'today':
#             start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#             end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
#         elif created_at.lower() == 'yesterday':
#             start_date = (timezone.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
#             end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
#         elif created_at.lower() == '1 week ago':
#             start_date = (timezone.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
#             end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
#         elif created_at.lower() == '2 weeks ago':
#             start_date = (timezone.now() - timedelta(days=14)).replace(hour=0, minute=0, second=0, microsecond=0)
#             end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
#         elif created_at.lower() == '3 weeks ago':
#             start_date = (timezone.now() - timedelta(days=21)).replace(hour=0, minute=0, second=0, microsecond=0)
#             end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
#         elif created_at.lower() == 'this month':
#             start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#             end_date = timezone.now().replace(day=datetime.now().day, hour=23, minute=59, second=59, microsecond=999999)
#         elif created_at.lower() == 'last month':
#             last_month_end_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
#             last_month_start_date = last_month_end_date.replace(day=1)
#             start_date = last_month_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
#             end_date = last_month_end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
#         elif created_at.lower() == '1 month ago':
#             start_date = (timezone.now() - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
#             end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
#         elif created_at.lower() == '2 months ago':
#             start_date = (timezone.now() - timedelta(days=60)).replace(hour=0, minute=0, second=0, microsecond=0)
#             end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
#         elif created_at.lower() == '3 months ago':
#             start_date = (timezone.now() - timedelta(days=90)).replace(hour=0, minute=0, second=0, microsecond=0)
#             end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
#         elif created_at.lower() == '4 months ago':
#             start_date = (timezone.now() - timedelta(days=120)).replace(hour=0, minute=0, second=0, microsecond=0)
#             end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
#         elif created_at.lower() == '5 months ago':                                                                              
#             start_date = (timezone.now() - timedelta(days=150)).replace(hour=0, minute=0, second=0, microsecond=0)
#             end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
#         else:
#             raise ValueError("Invalid relative date string")

#         return start_date, end_date


# LANGUAGE_UUID_TO_CODE = {
#     "88aff31a-23c4-11ef-85c8-00e04ca50182": "en",  # English
#     "d81f50a8-af49-11ef-b29b-00e04ca50182": "te",# Telugu
#     "d14c42ad-af49-11ef-87d6-00e04ca50182":"hi", # Hindi
#     "f245f0ea-af49-11ef-9f6f-00e04ca50182":"ta",#tamil
#     "ddce67ed-af49-11ef-bc43-00e04ca50182":"ka" ,#kanada
#     "e3c3aa7c-af49-11ef-a280-00e04ca50182":"ml", #Malayalam
#     "ecacf67f-af49-11ef-9e94-00e04ca50182" :"ma", #Marathi
#     # Add other UUIDs here
# }

# class GetItemByfield_InputView(APIView):
#     serializer_class = NewsCategorySerializer1
#     pagination_class = CustomPagination

#     def get(self, request, *args, **kwargs):

#         # Base queryset
#         queryset = NewsCategory.objects.filter(
#             status="SUCCESS",
#             is_published="PUBLISHED"
#         ).order_by("-created_at")

#         # Filters
#         category_id = request.query_params.get("category_id")
#         news_sub_category_id = request.query_params.get("news_sub_category_id")
#         created_at = request.query_params.get("created_at")
#         language_id = request.query_params.get("language")

#         if category_id:
#             queryset = queryset.filter(
#                 Q(category_id=category_id) |
#                 Q(news_sub_category_id=category_id)
#             )

#         if news_sub_category_id:
#             queryset = queryset.filter(news_sub_category_id=news_sub_category_id)

#         if created_at:
#             start, end = self.get_date_range(created_at)
#             queryset = queryset.filter(created_at__range=(start, end))

#         # TARGET LANGUAGE CODE
#         target_lang = LANGUAGE_UUID_TO_CODE.get(language_id, "en")

#         # PAGINATE
#         paginator = self.pagination_class()
#         page = paginator.paginate_queryset(queryset, request)

#         results = []

#         for obj in page:
#             data = self.serializer_class(obj).data

#             # extract text safely
#             headline = data.get("headline") or ""
#             desc = data.get("desc") or ""
#             short_description = data.get("short_description") or ""

#             # translate
#             if target_lang != "en":
#                 data["headline"] = translate_text_sarvam(headline, target_lang)
#                 data["desc"] = translate_text_sarvam(desc, target_lang)
#                 data["short_description"] = translate_text_sarvam(short_description, target_lang)

#             results.append(data)

#         return paginator.get_paginated_response(results)

#     def get_date_range(self, created_at):
#         now = timezone.now()

#         if created_at.lower() == "today":
#             start = now.replace(hour=0, minute=0, second=0, microsecond=0)
#             end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
#         elif created_at.lower() == "yesterday":
#             start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
#             end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
#         else:
#             start = timezone.make_aware(datetime.strptime(created_at, "%Y-%m-%d"))
#             start = start.replace(hour=0, minute=0, second=0, microsecond=0)
#             end = start.replace(hour=23, minute=59, second=59, microsecond=999999)

#         return start, end

# class GetItemByfield_InputView(APIView):
#     serializer_class = NewsCategorySerializer1
#     pagination_class = CustomPagination

#     def get(self, request, *args, **kwargs):

#         queryset = NewsCategory.objects.filter(
#             status="SUCCESS",
#             is_published="PUBLISHED"
#         ).order_by("-created_at")

#         category_id = request.query_params.get("category_id")
#         news_sub_category_id = request.query_params.get("news_sub_category_id")
#         created_at = request.query_params.get("created_at")
#         language_id = request.query_params.get("language")

#         if category_id:
#             queryset = queryset.filter(
#                 Q(category_id=category_id) |
#                 Q(news_sub_category_id=category_id)
#             )

#         if news_sub_category_id:
#             queryset = queryset.filter(news_sub_category_id=news_sub_category_id)

#         if created_at:
#             start, end = self.get_date_range(created_at)
#             queryset = queryset.filter(created_at__range=(start, end))

#         target_lang = LANGUAGE_UUID_TO_CODE.get(language_id, "en")

#         paginator = self.pagination_class()
#         page = paginator.paginate_queryset(queryset, request)

#         results = []

#         for obj in page:
#             data = self.serializer_class(obj).data
#             headline = data.get("headline") or ""
#             desc = data.get("desc") or ""
#             short_description = data.get("short_description") or ""

#             # Translate if needed
#             if target_lang != "en":
#                 headline = translate_text_sarvam(headline, target_lang)
#                 desc = translate_text_sarvam(desc, target_lang)
#                 short_description = translate_text_sarvam(short_description, target_lang)

#             # Generate audio for TTS (always)
#             audio_url = generate_speech_sarvam(desc or headline, target_lang)

#             data.update({
#                 "headline": headline,
#                 "desc": desc,
#                 "short_description": short_description,
#                 "audio_url": audio_url
#             })

#             results.append(data)

#         return paginator.get_paginated_response(results)

#     def get_date_range(self, created_at):
#         now = timezone.now()
#         if created_at.lower() == "today":
#             start = now.replace(hour=0, minute=0, second=0, microsecond=0)
#             end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
#         elif created_at.lower() == "yesterday":
#             start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
#             end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
#         else:
#             start = timezone.make_aware(datetime.strptime(created_at, "%Y-%m-%d"))
#             start = start.replace(hour=0, minute=0, second=0, microsecond=0)
#             end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
#         return start, end


#-------------------------sarvam multiple language code working for text---------------------------------


LANGUAGE_UUID_TO_CODE = {
    "88aff31a-23c4-11ef-85c8-00e04ca50182": "en",
    "d14c42ad-af49-11ef-87d6-00e04ca50182": "hi",
    "d81f50a8-af49-11ef-b29b-00e04ca50182": "te",
    "ddce67ed-af49-11ef-bc43-00e04ca50182": "kn",
    "e3c3aa7c-af49-11ef-a280-00e04ca50182": "ml",
    "ecacf67f-af49-11ef-9e94-00e04ca50182": "mr",
    "f245f0ea-af49-11ef-9f6f-00e04ca50182": "ta",
    "88dcde1e-358f-41cf-bb0a-83b5b86e0c05": "as",
    "9f527116-f3ff-4353-8132-42865610b1c7": "or"
}
class GetItemByfield_InputView(APIView):
    serializer_class = NewsCategorySerializer1
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        queryset = NewsCategory.objects.filter(
            status="SUCCESS",
            is_published="PUBLISHED"
        ).order_by("-created_at")
        news_id = request.query_params.get("_id")
        category_id = request.query_params.get("category_id")
        news_sub_category_id = request.query_params.get("news_sub_category_id")
        created_at = request.query_params.get("created_at")
        language_id = request.query_params.get("language")

        if news_id:
            queryset = queryset.filter(_id=news_id)

        if category_id:
            queryset = queryset.filter(
                Q(category_id=category_id) |
                Q(news_sub_category_id=category_id)
            )

        if news_sub_category_id:
            queryset = queryset.filter(news_sub_category_id=news_sub_category_id)

        if created_at:
            start, end = self.get_date_range(created_at)
            queryset = queryset.filter(created_at__range=(start, end))

        target_lang = LANGUAGE_UUID_TO_CODE.get(language_id, "en")

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        results = []

        for obj in page:
            data = self.serializer_class(obj).data

            headline = data.get("headline") or ""
            short_description = data.get("short_description") or ""
            desc = data.get("desc") or ""

            # Translate text
            if target_lang != "en":
                headline = translate_text_sarvam(headline, target_lang) or headline
                short_description = translate_text_sarvam(short_description, target_lang) or short_description
                desc = self.translate_long_text(desc, target_lang)

            # Generate audio for long text
            audio_url = generate_speech_sarvam(desc or headline, target_lang)

            # Update data
            data.update({
                "headline": headline,
                "desc": desc,
                "short_description": short_description,
                "audio_url": audio_url,
                "news_sub_category_id": data.get("news_sub_category_id")  # keep null if null
            })

            results.append(data)

        return paginator.get_paginated_response(results)

    def translate_long_text(self, text, target_lang):
        """Translate long text in chunks to avoid API limits"""
        max_len = 1000
        translated = ""
        for i in range(0, len(text), max_len):
            chunk = text[i:i+max_len]
            translated_chunk = translate_text_sarvam(chunk, target_lang)
            translated += translated_chunk or chunk
        return translated

    # def generate_audio_for_long_text(self, text, lang="en"):
    #     """Generate audio in chunks for long text to avoid TTS limits"""
    #     chunk_size = 400
    #     audio_urls = []
    #     for i in range(0, len(text), chunk_size):
    #         chunk = text[i:i+chunk_size]
    #         try:
    #             url = generate_speech_sarvam(chunk, lang)
    #             if url:
    #                 audio_urls.append(url)
    #         except Exception as e:
    #             print("TTS chunk failed:", e)
    #             continue
    #     return audio_urls

    def get_date_range(self, created_at):
        now = timezone.now()
        if created_at.lower() == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif created_at.lower() == "yesterday":
            start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            start = timezone.make_aware(datetime.strptime(created_at, "%Y-%m-%d"))
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start, end












# from django.core.cache import cache
# from rest_framework.views import APIView
# from django.utils import timezone
# from datetime import datetime, timedelta
# from django.db.models import Q
# from rest_framework.response import Response

# CACHE_TTL = 60 * 60 * 24  # 24 hours


# class GetItemByfield_InputView(APIView):
#     serializer_class = NewsCategorySerializer1
#     pagination_class = CustomPagination

#     def get(self, request, *args, **kwargs):

#         queryset = NewsCategory.objects.filter(
#             status="SUCCESS",
#             is_published="PUBLISHED"
#         ).order_by("-created_at")

#         category_id = request.query_params.get("category_id")
#         news_sub_category_id = request.query_params.get("news_sub_category_id")
#         created_at = request.query_params.get("created_at")
#         language_id = request.query_params.get("language")

#         if category_id:
#             queryset = queryset.filter(
#                 Q(category_id=category_id) |
#                 Q(news_sub_category_id=category_id)
#             )

#         if news_sub_category_id:
#             queryset = queryset.filter(news_sub_category_id=news_sub_category_id)

#         if created_at:
#             start, end = self.get_date_range(created_at)
#             queryset = queryset.filter(created_at__range=(start, end))

#         target_lang = LANGUAGE_UUID_TO_CODE.get(language_id, "en")

#         paginator = self.pagination_class()
#         page = paginator.paginate_queryset(queryset, request)

#         results = []

#         # ----------------------------------------------------
#         # 1) COLLECT all short texts for batch translation
#         # ----------------------------------------------------
#         small_texts = []
#         for obj in page:
#             data = self.serializer_class(obj).data

#             if target_lang != "en":
#                 if data.get("headline"):
#                     small_texts.append(data["headline"])
#                 if data.get("short_description"):
#                     small_texts.append(data["short_description"])

#         # ----------------------------------------------------
#         # 2) BATCH TRANSLATE small texts (single API call)
#         # ----------------------------------------------------
#         if target_lang != "en" and small_texts:
#             small_texts = list(set(small_texts))  # remove duplicates
#             small_translations = self.batch_translate(small_texts, target_lang)
#         else:
#             small_translations = {}

#         # ----------------------------------------------------
#         # 3) PROCESS EACH NEWS ITEM
#         # ----------------------------------------------------
#         for obj in page:
#             data = self.serializer_class(obj).data

#             headline = data.get("headline") or ""
#             short_description = data.get("short_description") or ""
#             desc = data.get("desc") or ""

#             # ------------------------
#             # Translation (optimized)
#             # ------------------------
#             if target_lang != "en":

#                 # Use cached batch translations
#                 headline = small_translations.get(headline, headline)
#                 short_description = small_translations.get(short_description, short_description)

#                 # Translate long text only if needed
#                 if len(desc) > 0:
#                     desc = self.translate_long_text_cached(desc, target_lang)

#             # ------------------------
#             # AUDIO (optimized)
#             # ------------------------
#             if len(desc) > 500:
#                 # Skip audio for long texts
#                 audio_url = None
#             else:
#                 audio_url = self.get_cached_audio(desc or headline, target_lang)

#             # Update response
#             data.update({
#                 "headline": headline,
#                 "desc": desc,
#                 "short_description": short_description,
#                 "audio_url": audio_url,
#                 "news_sub_category_id": data.get("news_sub_category_id")
#             })

#             results.append(data)

#         return paginator.get_paginated_response(results)

#     # --------------------------------------------------------------
#     #   BATCH TRANSLATION (Single API call)
#     # --------------------------------------------------------------
#     def batch_translate(self, texts, lang):
#         """
#         Translate multiple short texts in one API call.
#         Cache each translation separately.
#         """
#         translated_dict = {}

#         for text in texts:
#             cache_key = f"translation:{lang}:{text}"
#             cached_value = cache.get(cache_key)
#             if cached_value:
#                 translated_dict[text] = cached_value
#             else:
#                 result = translate_text_sarvam(text, lang)
#                 translated = result or text
#                 translated_dict[text] = translated
#                 cache.set(cache_key, translated, CACHE_TTL)

#         return translated_dict

#     # --------------------------------------------------------------
#     #   Long text translation with chunking + cache
#     # --------------------------------------------------------------
#     def translate_long_text_cached(self, text, lang):
#         cache_key = f"long_translation:{lang}:{hash(text)}"
#         cached_value = cache.get(cache_key)
#         if cached_value:
#             return cached_value

#         max_len = 1000
#         translated = ""

#         for i in range(0, len(text), max_len):
#             chunk = text[i:i+max_len]
#             translated_chunk = translate_text_sarvam(chunk, lang)
#             translated += (translated_chunk or chunk)

#         cache.set(cache_key, translated, CACHE_TTL)
#         return translated

#     # --------------------------------------------------------------
#     #   Cached TTS (Audio)
#     # --------------------------------------------------------------
#     def get_cached_audio(self, text, lang):
#         cache_key = f"audio:{lang}:{hash(text)}"
#         cached_value = cache.get(cache_key)
#         if cached_value:
#             return cached_value

#         audio_url = generate_speech_sarvam(text, lang)
#         cache.set(cache_key, audio_url, CACHE_TTL)
#         return audio_url

#     def get_date_range(self, created_at):
#         now = timezone.now()
#         if created_at.lower() == "today":
#             start = now.replace(hour=0, minute=0, second=0, microsecond=0)
#             end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
#         elif created_at.lower() == "yesterday":
#             start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
#             end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
#         else:
#             start = timezone.make_aware(datetime.strptime(created_at, "%Y-%m-%d"))
#             start = start.replace(hour=0, minute=0, second=0, microsecond=0)
#             end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
#         return start, end








class UpdateNewsStatus(generics.GenericAPIView):
    serializer_class = NewsCategorySerializer2

    def put(self, request, _id):
       
        instance = get_object_or_404(NewsCategory, _id=_id)
        
        serializer = NewsCategorySerializer2(instance, data=request.data)
        
        serializer.is_valid(raise_exception=True)
        
        instance = serializer.save()
        
        return Response(NewsCategorySerializer2(instance).data, status=status.HTTP_200_OK)




from fuzzywuzzy import process, fuzz
from rest_framework import generics
from django.db.models import Q




class SearchNews(generics.ListAPIView):
    serializer_class = NewsCategorySerializer1
    pagination_class = CustomPagination

    def get_queryset(self):
        query = self.request.query_params.get('search', '').strip()
        if query:
            return self.fuzzy_search(query)
        return NewsCategory.objects.none()  # Return empty if no search term is provided
    


    def fuzzy_search(self, query):
        all_news = NewsCategory.objects.filter(status="SUCCESS").values('_id', 'headline', 'desc')
        news_list = [(news['_id'], news['headline'] or "", news['desc'] or "") for news in all_news]
    
        # Lower threshold to allow matching even with slight misspellings
        threshold = 60
        matched_ids = set()
    
        # Fuzzy match for headlines
        headlines = [news[1] for news in news_list]
        print("Headlines:", headlines)
        
        headline_matches = process.extract(query, headlines, limit=20, scorer=fuzz.token_set_ratio)
        print("Token set ratio headline matches:", headline_matches)
        
        partial_headline_matches = process.extract(query, headlines, limit=20, scorer=fuzz.partial_ratio)
        print("Partial ratio headline matches:", partial_headline_matches)
        
        sort_headline_matches = process.extract(query, headlines, limit=20, scorer=fuzz.token_sort_ratio)
        print("Token sort ratio headline matches:", sort_headline_matches)
    
        all_headline_matches = headline_matches + partial_headline_matches + sort_headline_matches
    
        matched_headline_ids = [
            news[0] for news in news_list if any(
                match[0] == news[1] and match[1] >= threshold for match in all_headline_matches
            )
        ]
        print("Matched headline IDs:", matched_headline_ids)
        matched_ids.update(matched_headline_ids)
    
        # Fuzzy match for descriptions
        descriptions = [news[2] for news in news_list]
        print("Descriptions:", descriptions)
        
        desc_matches = process.extract(query, descriptions, limit=20, scorer=fuzz.token_set_ratio)
        print("Token set ratio description matches:", desc_matches)
        
        partial_desc_matches = process.extract(query, descriptions, limit=20, scorer=fuzz.partial_ratio)
        print("Partial ratio description matches:", partial_desc_matches)
        
        sort_desc_matches = process.extract(query, descriptions, limit=20, scorer=fuzz.token_sort_ratio)
        print("Token sort ratio description matches:", sort_desc_matches)
    
        all_desc_matches = desc_matches + partial_desc_matches + sort_desc_matches
    
        matched_desc_ids = [
            news[0] for news in news_list if any(
                match[0] == news[2] and match[1] >= threshold for match in all_desc_matches
            )
        ]
        print("Matched description IDs:", matched_desc_ids)
        matched_ids.update(matched_desc_ids)
    
        print("Final matched IDs:", matched_ids)
    
        return NewsCategory.objects.filter(_id__in=matched_ids)
    


    # def fuzzy_search(self, query):
    #     all_news = NewsCategory.objects.all().values('_id', 'headline', 'desc')
    #     news_list = [(news['_id'], news['headline'], news['desc']) for news in all_news]

    #     # Lower threshold to allow matching even with slight misspellings
    #     threshold = 60
    #     matched_ids = set()

    #     # Fuzzy match for headlines
    #     headlines = [news[1] for news in news_list]
    #     print("Headlines:", headlines)
        
    #     headline_matches = process.extract(query, headlines, limit=20, scorer=fuzz.token_set_ratio)
    #     print("Token set ratio headline matches:", headline_matches)
        
    #     # Additional matchers to handle variations
    #     partial_headline_matches = process.extract(query, headlines, limit=20, scorer=fuzz.partial_ratio)
    #     print("Partial ratio headline matches:", partial_headline_matches)
        
    #     sort_headline_matches = process.extract(query, headlines, limit=20, scorer=fuzz.token_sort_ratio)
    #     print("Token sort ratio headline matches:", sort_headline_matches)

    #     # Combine all headline matches
    #     all_headline_matches = headline_matches + partial_headline_matches + sort_headline_matches

    #     # Filter out news items based on headline matches
    #     matched_headline_ids = [
    #         news[0] for news in news_list if any(
    #             match[0] == news[1] and match[1] >= threshold for match in all_headline_matches
    #         )
    #     ]
    #     print("Matched headline IDs:", matched_headline_ids)
    #     matched_ids.update(matched_headline_ids)

    #     # Fuzzy match for descriptions
    #     descriptions = [news[2] for news in news_list]
    #     print("Descriptions:", descriptions)
        
    #     desc_matches = process.extract(query, descriptions, limit=20, scorer=fuzz.token_set_ratio)
    #     print("Token set ratio description matches:", desc_matches)
        
    #     partial_desc_matches = process.extract(query, descriptions, limit=20, scorer=fuzz.partial_ratio)
    #     print("Partial ratio description matches:", partial_desc_matches)
        
    #     sort_desc_matches = process.extract(query, descriptions, limit=20, scorer=fuzz.token_sort_ratio)
    #     print("Token sort ratio description matches:", sort_desc_matches)

    #     # Combine all description matches
    #     all_desc_matches = desc_matches + partial_desc_matches + sort_desc_matches

    #     # Filter out news items based on description matches
    #     matched_desc_ids = [
    #         news[0] for news in news_list if any(
    #             match[0] == news[2] and match[1] >= threshold for match in all_desc_matches
    #         )
    #     ]
    #     print("Matched description IDs:", matched_desc_ids)
    #     matched_ids.update(matched_desc_ids)

    #     # Final set of matched IDs
    #     print("Final matched IDs:", matched_ids)

    #     # Fetch NewsCategory records with matched IDs
    #     return NewsCategory.objects.filter(_id__in=matched_ids)










########old code ################



# class StagingToProductionViewSet(viewsets.ModelViewSet):
#     # queryset = StagingModel.objects.all()
#     queryset = NewsCategory.objects.filter(status='SUCCESS',is_published='PUBLISHED')
#     serializer_class = StagingSerializer



#     @action(detail=False, methods=['post'], url_path='transfer_to_production/(?P<_id>[^/.]+)')
#     def transfer_to_production(self, request, _id=None):
#         if not _id:
#             return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             staging_record = get_object_or_404(StagingModel, _id=_id)
#         except StagingModel.DoesNotExist:
#             return Response({"error": "Record not found in staging database"}, status=status.HTTP_404_NOT_FOUND)

#         if staging_record.status != "SUCCESS":
#             return Response({"error": "Only records with status 'SUCCESS' can be transferred"}, status=status.HTTP_400_BAD_REQUEST)
        
#         if staging_record.category_id is None:
#             return Response({"error": "category_id cannot be null"}, status=status.HTTP_400_BAD_REQUEST)


#         try:
#             # Check if the record already exists in production
#             production_record, created = NewsCategory.objects.update_or_create(
#                 _id=staging_record._id,
#                 defaults={
#                     'headline': staging_record.headline,
#                     'desc': staging_record.desc,
#                     'short_description':staging_record.short_description,
#                     'location': staging_record.location,
#                     'status': staging_record.status,
#                     'category_id': staging_record.category_id,
#                     'news_sub_category_id': staging_record.news_sub_category_id,
#                     'image_location': staging_record.image_location,
#                     'audio_location': staging_record.audio_location,
#                     'media': staging_record.media,
#                     # 'language_id': staging_record.language_id,
#                     'language': staging_record.language,
#                     'user': staging_record.user,
#                     'url': staging_record.url,
#                     'publish_at':staging_record.publish_at,
#                     'is_published':staging_record.is_published
             
#                 }
#             )
#             message = "Data transferred to production successfully." if created else "Data updated in production successfully."
#             return Response({"message": message}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#     @action(detail=False, methods=['post'], url_path='transfer_to_staging/(?P<_id>[^/.]+)')
#     def transfer_to_staging(self, request, _id=None):
#         if not _id:
#             return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             production_record = get_object_or_404(NewsCategory, _id=_id)
#         except NewsCategory.DoesNotExist:
#             return Response({"error": "Record not found in production database"}, status=status.HTTP_404_NOT_FOUND)

#         try:
#             # Check if the record already exists in staging
#             staging_record, created = StagingModel.objects.update_or_create(
#                 _id=production_record._id,
#                 defaults={
#                     'headline': production_record.headline,
#                     'desc': production_record.desc,
#                     'short_description':production_record.short_description,
#                     'location': production_record.location,
#                     'status': production_record.status,
#                     'category_id': production_record.category_id,
#                     'news_sub_category_id': production_record.news_sub_category_id,
#                     'image_location': production_record.image_location,
#                     'audio_location': production_record.audio_location,
#                     'media': production_record.media,
#                     # 'language_id': production_record.language_id,
#                     'language': production_record.language,
#                     'user': production_record.user,
#                     'url': production_record.url,
#                     'publish_at':production_record.publish_at,
#                     'is_published':production_record.is_published
                   
#                 }
#             )

#             production_record.delete()
            
#             message = "Data transferred to staging successfully." if created else "Data updated in staging successfully."
#             return Response({"message": message}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..enums import LanguageEnum

class StagingToProductionViewSet(viewsets.ModelViewSet):
    queryset = StagingModel.objects.all()
    serializer_class = StagingSerializer

    @action(detail=False, methods=['post'], url_path='transfer_to_production/(?P<_id>[^/.]+)')
    def transfer_to_production(self, request, _id=None):
        if not _id:
            return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        staging_record = get_object_or_404(StagingModel, _id=_id)

        if staging_record.status != "SUCCESS":
            return Response({"error": "Only records with status 'SUCCESS' can be transferred"}, status=status.HTTP_400_BAD_REQUEST)

        if staging_record.category_id is None:
            return Response({"error": "category_id cannot be null"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            production_record, created = NewsCategory.objects.update_or_create(
                _id=staging_record._id,
                defaults={
                    'headline': staging_record.headline,
                    'desc': staging_record.desc,
                    'short_description': staging_record.short_description,
                    'location': staging_record.location,
                    'status': staging_record.status,
                    'category_id': staging_record.category_id,
                    'news_sub_category_id': staging_record.news_sub_category_id,
                    'image_location': staging_record.image_location,
                    'audio_location': staging_record.audio_location,
                    'media': staging_record.media,
                    'language': staging_record.language_id.name if staging_record.language_id else LanguageEnum.ENGLISH.value,
                    'user': staging_record.user,
                    'url': staging_record.url,
                    'publish_at': staging_record.publish_at,
                    'is_published': staging_record.is_published
                }
            )
            message = "Data transferred to production successfully." if created else "Data updated in production successfully."
            return Response({"message": message}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='transfer_to_staging/(?P<_id>[^/.]+)')
    def transfer_to_staging(self, request, _id=None):
        if not _id:
            return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        production_record = get_object_or_404(NewsCategory, _id=_id)

        try:
            staging_record, created = StagingModel.objects.update_or_create(
                _id=production_record._id,
                defaults={
                    'headline': production_record.headline,
                    'desc': production_record.desc,
                    'short_description': production_record.short_description,
                    'location': production_record.location,
                    'status': production_record.status,
                    'category_id': production_record.category_id,
                    'news_sub_category_id': production_record.news_sub_category_id,
                    'image_location': production_record.image_location,
                    'audio_location': production_record.audio_location,
                    'media': production_record.media,
                    'language_id': production_record.language_id if hasattr(production_record, 'language_id') else None,
                    'user': production_record.user,
                    'url': production_record.url,
                    'publish_at': production_record.publish_at,
                    'is_published': production_record.is_published
                }
            )

            production_record.delete()
            message = "Data transferred to staging successfully." if created else "Data updated in staging successfully."
            return Response({"message": message}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)












class ProductionViewSet(viewsets.ModelViewSet):
    queryset = NewsCategory.objects.all()
    serializer_class = NewsCategorySerializer3



class NewsPDFDownloadView(APIView):
    def get(self, request, news_id):
        try:
            # Fetch the news by ID
            news = NewsCategory.objects.get(_id=news_id)

            # Create a BytesIO buffer for the PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)

            # Create a stylesheet for the document
            stylesheet = getSampleStyleSheet()
            style_title = stylesheet['Heading1']
            style_body = stylesheet['Normal']
            style_body.fontSize = 12
            style_body.leading = 14
            style_body.fontName = "Helvetica"

            # Create a list to hold elements
            content = []

            # Add Headline Section
            title = f"News: {news.headline if news.headline else 'No Headline'}"
            title_paragraph = Paragraph(title, style_title)
            content.append(title_paragraph)
            content.append(Spacer(1, 12))  # Space after headline

            # Add Image Section
            if news.image_location:
                try:
                    # Parse the first image path
                    if isinstance(news.image_location, str):
                        image_paths = json.loads(news.image_location)  # Convert JSON string to list
                    elif isinstance(news.image_location, list):
                        image_paths = news.image_location
                    else:
                        image_paths = []

                    if image_paths:
                        first_image_path = image_paths[0]
                        full_image_url = f"{settings.FILE_URL}{first_image_path}"

                        # Log the URL for debugging
                        print(f"Fetching image from URL: {full_image_url}")

                        # Fetch the image from URL
                        response = requests.get(full_image_url, stream=True)

                        if response.status_code == 200:
                            # Successfully fetched the image
                            print("Image fetched successfully")

                            # Convert the image content to ImageReader
                            image = ImageReader(BytesIO(response.content))

                            # Set image size and position
                            image_height = 200
                            image_width = 400

                            # Add image to the PDF
                            content.append(Spacer(1, 12))  # Add space before the image
                            content.append(Image(BytesIO(response.content), width=image_width, height=image_height))
                            content.append(Spacer(1, 12))  # Add space after the image
                        else:
                            # If failed to fetch the image, add a message to the PDF
                            content.append(Paragraph(f"Failed to load image: HTTP {response.status_code}", style_body))
                            print(f"Error: Unable to fetch image (HTTP {response.status_code})")
                    else:
                        content.append(Paragraph("No valid image provided.", style_body))
                except Exception as e:
                    # Catching any other exceptions and logging
                    content.append(Paragraph(f"Error loading image: {str(e)}", style_body))
                    print(f"Error loading image: {str(e)}")
            else:
                content.append(Paragraph("No image provided.", style_body))

            # Add Description Section
            description = f"<b>Description:</b> {news.desc if news.desc else 'No description available.'}"
            description_paragraph = Paragraph(description, style_body)
            content.append(description_paragraph)
            content.append(Spacer(1, 12))  # Space after description

            # Add Location Section
            location_text = f"<b>Location:</b> {news.location if news.location else 'Not provided'}"
            location_paragraph = Paragraph(location_text, style_body)
            content.append(location_paragraph)
            content.append(Spacer(1, 12))  # Space after location

            # Footer section (optional)
            content.append(Spacer(1, 12))
            # footer = "Page generated by News Platform"
            # footer_paragraph = Paragraph(footer, style_body)
            # content.append(footer_paragraph)

            # Build the document
            doc.build(content)

            # Get the PDF contents
            buffer.seek(0)
            return HttpResponse(
                buffer,
                content_type='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename="{news.headline}.pdf"',
                }
            )
        except NewsCategory.DoesNotExist:
            return HttpResponse("News not found", status=404)
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)

from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from django.urls import reverse

class NewsDetailView(APIView):
    def get(self, request, news_id):
        try:
            # Fetch the news by ID
            news = NewsCategory.objects.get(_id=news_id)
            return JsonResponse({
                "headline": news.headline,
                "description": news.desc,
                "location": news.location,
                "created_at": news.created_at.strftime('%Y-%m-%d'),
            }, status=200)
        except NewsCategory.DoesNotExist:
            return JsonResponse({"status": "error", "message": "News not found"}, status=404)
        
from django.http import JsonResponse
from django.urls import reverse
from rest_framework.views import APIView
import json

class ShareNewsView(APIView):
    def get(self, request, news_id):
        try:
            # Fetch the news by ID
            news = NewsCategory.objects.get(_id=news_id)

            # Generate the custom share URL using the news ID
            share_url = f"https://hindupulse.com/latestnewsreadmore/{news_id}"

            # Handle image_location to get only the first image
            image_url = None
            if news.image_location:
                try:
                    # Parse the image location field (JSON string or list)
                    if isinstance(news.image_location, str):
                        image_paths = json.loads(news.image_location)  # Convert JSON string to list
                    elif isinstance(news.image_location, list):
                        image_paths = news.image_location
                    else:
                        image_paths = []

                    # Get the first image path and construct the full URL
                    if image_paths:
                        first_image_path = image_paths[0]
                        # Construct the full URL to the image
                        image_url = f"https://sathayushstorage.blob.core.windows.net/sathayush/{first_image_path}"

                except Exception as e:
                    # Handle parsing errors
                    image_url = "Error processing image location"

            # Create a shareable message
            share_message = {
                "headline": news.headline if news.headline else "No Headline",
                # "description": news.desc if news.desc else "No description available.",
                # "location": news.location if news.location else "Not provided",
                "image": image_url,
                "share_url": share_url,
                
            }

            return JsonResponse({
                "status": "success",
                "data": share_message,
            }, status=200)

        except NewsCategory.DoesNotExist:
            return JsonResponse({"status": "error", "message": "News not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        


# class SearchNewsByLocation(generics.ListAPIView):
#     serializer_class = NewsCategorySerializer1
#     pagination_class = CustomPagination

#     def get_queryset(self):
#         query = self.request.query_params.get('location', '').strip()

#         if not query:
#             return NewsCategory.objects.none()  # Return empty if no search term is provided

#         return self.fuzzy_search(query)

#     def fuzzy_search(self, query):
#         # Fetch all locations from the NewsCategory model
#         queryset = NewsCategory.objects.filter(status='SUCCESS')

#         all_news = queryset.order_by('-created_at').values('_id', 'location')
#         news_list = [(news['_id'], news['location'] or "") for news in all_news]

#         # Lower threshold to allow matching even with slight misspellings
#         threshold = 90
#         matched_ids = set()

#         # Fuzzy match for locations
#         locations = [news[1] for news in news_list]
#         print("Locations:", locations)

#         location_matches = process.extract(query, locations, limit=20, scorer=fuzz.token_set_ratio)
#         print("Token set ratio location matches:", location_matches)

#         partial_location_matches = process.extract(query, locations, limit=20, scorer=fuzz.partial_ratio)
#         print("Partial ratio location matches:", partial_location_matches)

#         sort_location_matches = process.extract(query, locations, limit=20, scorer=fuzz.token_sort_ratio)
#         print("Token sort ratio location matches:", sort_location_matches)

#         all_location_matches = location_matches + partial_location_matches + sort_location_matches

#         matched_location_ids = [
#             news[0] for news in news_list if any(
#                 match[0] == news[1] and match[1] >= threshold for match in all_location_matches
#             )
#         ]
#         print("Matched location IDs:", matched_location_ids)
#         matched_ids.update(matched_location_ids)

#         print("Final matched IDs:", matched_ids)

#         return NewsCategory.objects.filter(_id__in=matched_ids).order_by('-created_at')

# from fuzzywuzzy import process, fuzz
# from django.db.models import Q

# class SearchNewsByLocation(generics.ListAPIView):
#     serializer_class = NewsCategorySerializer1
#     pagination_class = CustomPagination

#     state_groups = {
#         "Bihar": ["Bihar", "Jharkhand"],
#         "Maharashtra": ["Maharashtra", "Goa"],
#         "Andhra Pradesh": ["Andhra Pradesh"],
#         "Chhattisgarh": ["Chhattisgarh"],
#         "Delhi": ["Delhi"],
#         "Gujarat": ["Gujarat"],
#         "Himachal Pradesh": ["Himachal Pradesh"],
#         "Haryana": ["Haryana"],
#         "Jammu And Kashmir": ["Jammu And Kashmir"],
#         "Kerala": ["Kerala"],
#         "Karnataka": ["Karnataka"],
#         "Madhya Pradesh": ["Madhya Pradesh"],
#         "Odisha": ["Odisha"],
#         "Punjab": ["Punjab"],
#         "Rajasthan": ["Rajasthan"],
#         "Telangana": ["Telangana"],
#         "Tamil Nadu": ["Tamil Nadu"],
#         "Uttar Pradesh": ["Uttar Pradesh"],
#         "West Bengal": ["West Bengal"],
#         "Uttarakhand": ["Uttarakhand"],
#         "North East States": [
#             "Assam", "Nagaland", "Manipur", "Tripura", "Mizoram", "Arunachal Pradesh", "Meghalaya"
#         ],
#     }

#     def get_queryset(self):
#         query = self.request.query_params.get('location', '').strip()

#         if not query:
#             return NewsCategory.objects.none()  # Return empty if no search term is provided

#         return self.fuzzy_search(query)

#     def fuzzy_search(self, query):
#         queryset = NewsCategory.objects.filter(status='SUCCESS')
#         all_news = queryset.order_by('-created_at').values('_id', 'location')
#         news_list = [(news['_id'], news['location'] or "") for news in all_news]

#         threshold = 90
#         matched_ids = set()

#         # Match query against the state_groups and their locations
#         matched_states = self.get_matched_states(query)
#         print("Matched states:", matched_states)

#         # Fuzzy matching for individual locations
#         locations = [news[1] for news in news_list]
#         location_matches = process.extract(query, locations, limit=20, scorer=fuzz.token_set_ratio)
#         partial_location_matches = process.extract(query, locations, limit=20, scorer=fuzz.partial_ratio)
#         sort_location_matches = process.extract(query, locations, limit=20, scorer=fuzz.token_sort_ratio)

#         all_location_matches = location_matches + partial_location_matches + sort_location_matches

#         matched_location_ids = [
#             news[0] for news in news_list if any(
#                 match[0] == news[1] and match[1] >= threshold for match in all_location_matches
#             )
#         ]
#         matched_ids.update(matched_location_ids)

#         # Add matches based on state_groups
#         if matched_states:
#             for state in matched_states:
#                 state_locations = self.state_groups.get(state, [])
#                 state_based_ids = [
#                     news[0] for news in news_list if news[1] in state_locations
#                 ]
#                 matched_ids.update(state_based_ids)

#         print("Final matched IDs:", matched_ids)

#         return NewsCategory.objects.filter(_id__in=matched_ids).order_by('-created_at')

#     def get_matched_states(self, query):
#         """Match the query to states or state groups."""
#         states = list(self.state_groups.keys())
#         state_matches = process.extract(query, states, limit=5, scorer=fuzz.token_set_ratio)
#         return [match[0] for match in state_matches if match[1] >= 90]





# class SearchNewsByLocation(generics.ListAPIView):
#     serializer_class = NewsCategorySerializer1
#     pagination_class = CustomPagination

#     state_groups = {
#         "Bihar": ["Bihar", "Jharkhand"],
#         "Maharashtra": ["Maharashtra", "Goa"],
#         "Andhra Pradesh": ["Andhra Pradesh"],
#         "Chhattisgarh": ["Chhattisgarh"],
#         "Delhi": ["Delhi"],
#         "Gujarat": ["Gujarat"],
#         "Himachal Pradesh": ["Himachal Pradesh"],
#         "Haryana": ["Haryana"],
#         "Jammu And Kashmir": ["Jammu And Kashmir"],
#         "Kerala": ["Kerala"],
#         "Karnataka": ["Karnataka"],
#         "Madhya Pradesh": ["Madhya Pradesh"],
#         "Odisha": ["Odisha"],
#         "Punjab": ["Punjab"],
#         "Rajasthan": ["Rajasthan"],
#         "Telangana": ["Telangana"],
#         "Tamil Nadu": ["Tamil Nadu"],
#         "Uttar Pradesh": ["Uttar Pradesh"],
#         "West Bengal": ["West Bengal"],
#         "Uttarakhand": ["Uttarakhand"],
#         "North East States": [
#             "Assam", "Nagaland", "Manipur", "Tripura", "Mizoram", "Arunachal Pradesh", "Meghalaya"
#         ],
#     }

#     def get_queryset(self):
#         query = self.request.query_params.get('location', '').strip()

#         if not query:
#             return NewsCategory.objects.none()  # Return empty if no search term is provided

#         return self.location_search(query)

#     def location_search(self, query):
#         queryset = NewsCategory.objects.filter(status='SUCCESS')
#         all_news = queryset.order_by('-created_at').values('_id', 'location')

#         # Normalize input query and locations in the database
#         normalized_query = self.normalize_location(query)
#         print("Normalized query:", normalized_query)

#         normalized_news = [
#             (news['_id'], self.normalize_location(news['location'] or ""))
#             for news in all_news
#         ]
#         print("Normalized news:", normalized_news)

#         # Prepare state group and direct matches
#         matched_states = self.get_matched_states(normalized_query)
#         print("Matched states:", matched_states)

#         # Locations related to matched states
#         related_locations = set()
#         for state in matched_states:
#             related_locations.update(self.state_groups.get(state, []))
#         print("Related locations:", related_locations)

#         # Normalize related locations
#         normalized_related_locations = {self.normalize_location(loc) for loc in related_locations}
#         print("Normalized related locations:", normalized_related_locations)

#         # Filter IDs based on direct matches and related locations
#         matched_ids = set()
#         for news_id, location in normalized_news:
#             # Direct location match
#             if location == normalized_query:
#                 matched_ids.add(news_id)

#             # Location in related group
#             if location in normalized_related_locations:
#                 matched_ids.add(news_id)

#         print("Final matched IDs:", matched_ids)

#         # Return filtered queryset
#         return NewsCategory.objects.filter(_id__in=matched_ids).order_by('-created_at')

#     def normalize_location(self, location):
#         """Normalize location strings by converting to lowercase and stripping unwanted parts."""
#         return location.lower().replace(", india", "").strip()

#     def get_matched_states(self, query):
#         """Match the query to a state in the state_groups."""
#         states = list(self.state_groups.keys())
#         state_matches = process.extract(query, states, limit=5, scorer=fuzz.token_set_ratio)
#         print("State matches:", state_matches)

#         # Match states based on threshold
#         threshold = 90
#         matched_states = [
#             match[0] for match in state_matches if match[1] >= threshold
#         ]
#         return matched_states




class SearchNewsByLocation(generics.ListAPIView):
    serializer_class = NewsCategorySerializer1
    pagination_class = CustomPagination

    state_groups = {
            "Bihar": ["Bihar"],
            "Jharkhand": ["Jharkhand"],
            "Maharashtra": ["Maharashtra"],
            "Goa": ["Goa"],
            "Andhra Pradesh": ["Andhra Pradesh"],
            "Chhattisgarh": ["Chhattisgarh"],
            "Delhi": ["Delhi"],
            "Gujarat": ["Gujarat"],
            "Himachal Pradesh": ["Himachal Pradesh"],
            "Haryana": ["Haryana"],
            "Jammu and Kashmir and Ladakh": ["Jammu And Kashmir", "Ladakh"],
            "Kerala": ["Kerala"],
            "Karnataka": ["Karnataka"],
            "Madhya Pradesh": ["Madhya Pradesh"],
            "Odisha": ["Odisha"],
            "Punjab and Chandigarh": ["Punjab", "Chandigarh"],
            "Rajasthan": ["Rajasthan"],
            "Telangana": ["Telangana"],
            "Tamil Nadu": ["Tamil Nadu"],
            "Uttar Pradesh": ["Uttar Pradesh"],
            "West Bengal": ["West Bengal"],
            "Uttarakhand": ["Uttarakhand"],
            "North East States": [
                "Assam", "Nagaland", "Manipur", "Tripura", "Mizoram", "Arunachal Pradesh", "Meghalaya", "Sikkim"
            ],
            "Union Territories": [
                "Puducherry", "Andaman and Nicobar Islands","Dadra and Nagar Haveli and Daman and Diu","Lakshadweep",
            ]
        }

    def get_queryset(self):
        query = self.request.query_params.get('location', '').strip()

        if not query:
            return NewsCategory.objects.none()  # Return empty if no search term is provided

        return self.location_search(query)

    def location_search(self, query):
        queryset = NewsCategory.objects.filter(status='SUCCESS',is_published='PUBLISHED')
        all_news = queryset.order_by('-created_at').values('_id', 'location')

        # Normalize input query
        normalized_query = self.normalize_location(query)
        print("Normalized query:", normalized_query)

        normalized_news = [
            (news['_id'], self.split_and_normalize_location(news['location'] or ""))
            for news in all_news
        ]
        print("Normalized news:", normalized_news)

        # Prepare state group and direct matches
        matched_states = self.get_matched_states(normalized_query)
        print("Matched states:", matched_states)

        # Locations related to matched states
        related_locations = set()
        for state in matched_states:
            related_locations.update(self.state_groups.get(state, []))
        print("Related locations:", related_locations)

        # Normalize related locations
        normalized_related_locations = {self.normalize_location(loc) for loc in related_locations}
        print("Normalized related locations:", normalized_related_locations)

        # Filter IDs based on matches
        matched_ids = set()
        for news_id, locations in normalized_news:
            # Check each part of the split location
            for location in locations:
                # Direct location match
                if location == normalized_query:
                    matched_ids.add(news_id)

                # Location in related group
                if location in normalized_related_locations:
                    matched_ids.add(news_id)

        print("Final matched IDs:", matched_ids)

        # Return filtered queryset
        return NewsCategory.objects.filter(_id__in=matched_ids).order_by('-created_at')

    def normalize_location(self, location):
        """Normalize location strings by converting to lowercase and stripping unwanted parts."""
        return location.lower().replace(", india", "").strip()

    def split_and_normalize_location(self, location):
        """
        Split location into multiple parts and normalize each part.
        For example, 'Bihar&Jharkhand, India' becomes ['bihar', 'jharkhand'].
        """
        separators = ['&', ',', '/']  # Define common separators
        for sep in separators:
            if sep in location:
                parts = [self.normalize_location(part) for part in location.split(sep)]
                return parts
        return [self.normalize_location(location)]  # Single location case

    def get_matched_states(self, query):
        """Match the query to a state in the state_groups."""
        states = list(self.state_groups.keys())
        state_matches = process.extract(query, states, limit=5, scorer=fuzz.token_set_ratio)
        print("State matches:", state_matches)

        # Match states based on threshold
        threshold = 90
        matched_states = [
            match[0] for match in state_matches if match[1] >= threshold
        ]
        return matched_states
