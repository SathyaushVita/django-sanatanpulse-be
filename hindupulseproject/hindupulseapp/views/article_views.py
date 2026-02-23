
from rest_framework import viewsets
from ..models import ArticleModel,Register,ArticleProfile
from rest_framework .response import Response
from ..serializers import ArticleSerializer,ArticleSerializer1
from rest_framework import generics
from django.utils.timesince import timesince
from ..utils import save_image_to_azure,save_image_to_azure_v2,save_audio_to_azure
from django.utils.timezone import now, localtime
from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework import status
from datetime import datetime, timedelta
from rest_framework.views import APIView 
from django.utils import timezone
# from ..pagination import CustomPagination
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from ..enums.member_status_enum import MemberStatus
import re
from django.conf import settings
from django.core.mail import send_mail

from rest_framework.pagination import PageNumberPagination

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.utils import ImageReader
import requests


class ArticlesCustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = ArticleModel.objects.filter(status='SUCCESS').order_by('-created_at')
    serializer_class=ArticleSerializer1
    paginator = ArticlesCustomPagination()


class AddArticle(generics.GenericAPIView):
    serializer_class = ArticleSerializer

     
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

    # permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        article_user_id = request.data.get('article_user')
        print("hhhhhhhhhh",article_user_id)
        try:
            user = Register.objects.get(id=user_id)
            print(user, "5ttttttttttttttttt")
            if user.is_member != MemberStatus.true.value:  # Assuming MemberStatus.TRUE.value is how you define 'TRUE' in your enum
                print(user.is_member, "9uuuuuuuuuuuuuu")
                return JsonResponse({"error": "User is not a member"}, status=400)
        except Register.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        

        try:
            article_user = ArticleProfile.objects.get(id=article_user_id)
            if article_user.is_member != MemberStatus.true.value:
                return JsonResponse({"error": "Article user is not a member"}, status=status.HTTP_400_BAD_REQUEST)
        except ArticleProfile.DoesNotExist:
            return JsonResponse({"error": "Article user not found"}, status=status.HTTP_404_NOT_FOUND)
        audio_location = request.data.get('audio_location')  # New audio location
        image_location = request.data.get('image_location', [])
        if not isinstance(image_location, list):
            return JsonResponse({"error": "Image location must be a list"}, status=400)
        if len(image_location) > 1:
            return JsonResponse({"error": "You cannot upload more than one image"}, status=400)
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
        subject = 'New Article Added'
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


class EditArticle(generics.GenericAPIView):
    serializer_class = ArticleSerializer
     
    
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
        instance = get_object_or_404(ArticleModel, _id=_id)
        # pdf_location = request.data.get('pdf_location')
        audio_location = request.data.get('audio_location')  # New audio location

        mutable_data = request.data.copy()
        # mutable_data['pdf_location'] = "null"
        mutable_data['audio_location'] = "null"
        serializer = self.get_serializer(instance, data=mutable_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        if audio_location and audio_location != "null":  # Handle audio upload
            saved_audio_location = save_audio_to_azure(audio_location, serializer.instance._id, serializer.instance.category_id.name, "news")
            if saved_audio_location:
                serializer.instance.audio_location = saved_audio_location
                serializer.instance.save()
        # if pdf_location and pdf_location != "null":
        #     saved_location = save_pdf_to_azure(pdf_location, serializer.instance._id, serializer.instance.category_id.name, "article")
        #     if saved_location:
        #         serializer.instance.pdf_location = saved_location
        #         serializer.instance.save()

        # Update NewsCategory
        instance_news = get_object_or_404(ArticleModel, _id=_id)
        image_location = request.data.get('image_location', [])
        if not isinstance(image_location, list):
            return JsonResponse({"error": "Image location must be a list"}, status=400)
        if len(image_location) > 1:
            return JsonResponse({"error": "You cannot upload more than one image"}, status=400)
        mutable_data_news = request.data.copy()
        mutable_data['image_location'] = []
        serializer_news = self.get_serializer(instance_news, data=mutable_data_news)
        serializer_news.is_valid(raise_exception=True)
        serializer_news.save()

        saved_image_paths = []
        for idx, image_data in enumerate(image_location):
            if image_data:
                saved_location = save_image_to_azure_v2(image_data, serializer.instance._id, 'news', f'image{idx + 1}')
                if saved_location:
                    saved_image_paths.append(saved_location)

        if saved_image_paths:
            serializer.instance.image_location = saved_image_paths
            serializer.instance.save()
        subject = 'Edit Article Added'
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

    
class GetArticlesByDateView(APIView):
    serializer_class = ArticleSerializer1
    pagination_class = ArticlesCustomPagination

    def get(self, request, *args, **kwargs):
  
        queryset = ArticleModel.objects.filter(status='SUCCESS').order_by('-created_at')



        _id = request.query_params.get('_id')
        author = request.query_params.get('author')
        created_at = request.query_params.get('created_at')
        date = request.query_params.get('date')
        article_user= request.query_params.get('article_user')
        category_id = request.query_params.get('category_id')
        article_user_name = request.query_params.get('article_user_name')

        if article_user_name:
            queryset = queryset.filter(article_user__name=article_user_name)

        
        if article_user:
            queryset = queryset.filter(article_user=article_user)

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if _id:
            queryset = queryset.filter(_id=_id)
        if author:
            queryset = queryset.filter(author=author)
        if date:
            queryset = queryset.filter(date=date)


        # Filter by news_sub_category_id if provided
       
        if created_at:
            try:
                if created_at.lower() == 'today':
                    start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
                elif created_at.lower() == 'yesterday':
                    start_date = (timezone.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                elif created_at.lower() in ['1 week ago', '2 weeks ago', '3 weeks ago', 'this month', 'last month',
                                            '1 month ago', '2 months ago', '3 months ago', '4 months ago', '5 months ago']:
                    # Handle specific date ranges
                    start_date, end_date = self.get_date_range(created_at)
                else:
                    # Handle specific date format YYYY-MM-DD
                    start_date = timezone.make_aware(datetime.strptime(created_at, '%Y-%m-%d'), timezone.get_current_timezone())
                    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)

                # Check if start_date is older than 4 months from now
                if start_date < timezone.now() - timedelta(days=120):
                    return Response({
                        'message': 'No data available older than 4 months. All data has been cleared.',
                        'status': 204  # Custom status code indicating no content
                    }, status=status.HTTP_204_NO_CONTENT)

            except ValueError:
                return Response({
                    'message': 'Invalid date format',
                    'status': 400
                }, status=status.HTTP_400_BAD_REQUEST)

            queryset = queryset.filter(created_at__range=(start_date, end_date))

        # Pagination
        paginator = ArticlesCustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ArticleSerializer1(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)



# class LatestArticleNewsView(generics.ListAPIView):
#     serializer_class = ArticleSerializer1

#     def get(self, request, *args, **kwargs):
#         result = {}
#         articles = ArticleModel.objects.filter(status='SUCCESS').order_by('-created_at')[:5]  # Fetch the latest article

#         serializer = self.get_serializer(articles, many=True)
#         result["latest_articles"] = serializer.data
        
#         response_data = {
#             # "status": "success",
#             "result": result
#         }
#         return Response(response_data)

class LatestArticleNewsView(generics.ListAPIView):
    serializer_class = ArticleSerializer1

    def get(self, request, *args, **kwargs):
        result = {}
        # Fetch all articles with status 'SUCCESS', ordered by 'created_at' in descending order
        articles = ArticleModel.objects.filter(status='SUCCESS').order_by('-created_at')[:30]

        serializer = self.get_serializer(articles, many=True)
        result["latest_articles"] = serializer.data
        
        response_data = {
            # "status": "success",
            "result": result
        }
        return Response(response_data)




from django.http import HttpResponse

from io import BytesIO

class ArticlesPDFDownloadView(APIView):
    def get(self, request, articles_id):
        try:
            # Fetch the news by ID
            articles = ArticleModel.objects.get(_id=articles_id)

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
            title = f"Articles: {articles.headline if articles.headline else 'No Headline'}"
            title_paragraph = Paragraph(title, style_title)
            content.append(title_paragraph)
            content.append(Spacer(1, 12))  # Space after headline

            # Add Image Section
            if articles.image_location:
                try:
                    # Parse the first image path
                    if isinstance(articles.image_location, str):
                        image_paths = json.loads(articles.image_location)  # Convert JSON string to list
                    elif isinstance(articles.image_location, list):
                        image_paths = articles.image_location
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
            description = f"<b>Description:</b> {articles.desc if articles.desc else 'No description available.'}"
            description_paragraph = Paragraph(description, style_body)
            content.append(description_paragraph)
            content.append(Spacer(1, 12))  # Space after description

            # Add Location Section
            # location_text = f"<b>Location:</b> {articles.location if articles.location else 'Not provided'}"
            # location_paragraph = Paragraph(location_text, style_body)
            # content.append(location_paragraph)
            # content.append(Spacer(1, 12))  # Space after location

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
                    'Content-Disposition': f'attachment; filename="{articles.headline}.pdf"',
                }
            )
        except ArticleModel.DoesNotExist:
            return HttpResponse("Articles not found", status=404)
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)

from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from django.urls import reverse

class ArticlesDetailView(APIView):
    def get(self, request, articles_id):
        try:
            # Fetch the news by ID
            articles = ArticleModel.objects.get(_id=articles_id)
            return JsonResponse({
                "headline": articles.headline,
                "description": articles.desc,
                # "location": articles.location,
                "created_at": articles.created_at.strftime('%Y-%m-%d'),
            }, status=200)
        except ArticleModel.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Article not found"}, status=404)
        
from django.http import JsonResponse
from django.urls import reverse
from rest_framework.views import APIView
import json

class ShareArticlesView(APIView):
    def get(self, request, articles_id):
        try:
            # Fetch the news by ID
            articles = ArticleModel.objects.get(_id=articles_id)

            # Generate the custom share URL using the news ID
            share_url = f"https://hindupulse.com/articlereadmore/{articles_id}"

            # Handle image_location to get only the first image
            image_url = None
            if articles.image_location:
                try:
                    # Parse the image location field (JSON string or list)
                    if isinstance(articles.image_location, str):
                        image_paths = json.loads(articles.image_location)  # Convert JSON string to list
                    elif isinstance(articles.image_location, list):
                        image_paths = articles.image_location
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
                "headline": articles.headline if articles.headline else "No Headline",
                # "description": news.desc if news.desc else "No description available.",
                # "location": news.location if news.location else "Not provided",
                "image": image_url,
                "share_url": share_url,
                
            }

            return JsonResponse({
                "status": "success",
                "data": share_message,
            }, status=200)

        except ArticleModel.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Articles not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        












































































##############################################################this is code for pdf_location #####################################
# from rest_framework import viewsets
# from ..models import ArticleModel,Register,ArticleProfile
# from rest_framework .response import Response
# from ..serializers import ArticleSerializer,ArticleSerializer1
# from rest_framework import generics
# from django.utils.timesince import timesince
# from ..utils import save_image_to_azure,save_pdf_to_azure
# from django.utils.timezone import now, localtime
# from datetime import timedelta
# from django.shortcuts import get_object_or_404
# from rest_framework import status
# from datetime import datetime, timedelta
# from rest_framework.views import APIView 
# from django.utils import timezone
# # from ..pagination import CustomPagination
# from rest_framework.permissions import IsAuthenticated
# from django.http import JsonResponse
# from ..enums.member_status_enum import MemberStatus
# import re
# from django.conf import settings
# from django.core.mail import send_mail

# from rest_framework.pagination import PageNumberPagination

# class ArticlesCustomPagination(PageNumberPagination):
#     page_size = 6
#     page_size_query_param = 'page_size'
#     max_page_size = 100


# class ArticleViewSet(viewsets.ModelViewSet):
#     queryset = ArticleModel.objects.filter(status='SUCCESS').order_by('-created_at')
#     serializer_class=ArticleSerializer1
#     paginator = ArticlesCustomPagination()


# class AddArticle(generics.GenericAPIView):
#     serializer_class = ArticleSerializer

     
#     permission_classes = []
#     def get_permissions(self):
#         if self.request.method in ['POST', 'PUT']:
#             return [IsAuthenticated()]
#         return super().get_permissions()
#     def is_email(self, username):
#         return re.match(r"[^@]+@gmail\.com$", username)
#     def send_email(self, email, subject, message):
#         from_email = settings.EMAIL_HOST_USER
#         recipient_list = [email]
#         try:
#             send_mail(subject, message, from_email, recipient_list)
#             print("Email sent successfully")
#         except Exception as e:
#             print(f"Failed to send email: {e}")

#     # permission_classes = [permissions.IsAuthenticated]
#     def post(self, request, *args, **kwargs):
#         user_id = request.user.id
#         article_user_id = request.data.get('article_user')
#         print("hhhhhhhhhh",article_user_id)
#         try:
#             user = Register.objects.get(id=user_id)
#             print(user, "5ttttttttttttttttt")
#             if user.is_member != MemberStatus.true.value:  # Assuming MemberStatus.TRUE.value is how you define 'TRUE' in your enum
#                 print(user.is_member, "9uuuuuuuuuuuuuu")
#                 return JsonResponse({"error": "User is not a member"}, status=400)
#         except Register.DoesNotExist:
#             return JsonResponse({"error": "User not found"}, status=404)
        

#         try:
#             article_user = ArticleProfile.objects.get(id=article_user_id)
#             if article_user.is_member != MemberStatus.true.value:
#                 return JsonResponse({"error": "Article user is not a member"}, status=status.HTTP_400_BAD_REQUEST)
#         except ArticleProfile.DoesNotExist:
#             return JsonResponse({"error": "Article user not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         pdf_location = request.data.get('pdf_location')
#         image_location = request.data.get('image_location')
        
#         # Make a mutable copy of request.data and set initial locations to "null"
#         mutable_data = request.data.copy()
#         mutable_data['pdf_location'] = "null"
#         mutable_data['image_location'] = "null"
        
#         # Instantiate the serializer with the mutable copy
#         serializer = self.get_serializer(data=mutable_data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         # Handle saving PDF location if provided
#         if pdf_location and pdf_location != "null":
#             saved_pdf_location = save_pdf_to_azure(pdf_location, serializer.instance._id, serializer.instance.category_id.name, "article")
#             if saved_pdf_location:
#                 serializer.instance.pdf_location = saved_pdf_location
#                 serializer.instance.save()

#         # Handle saving image location if provided
#         if image_location and image_location != "null":
#             saved_image_location = save_image_to_azure(image_location, serializer.instance._id, serializer.instance.category_id.name, "article")
#             if saved_image_location:
#                 serializer.instance.image_location = saved_image_location
#                 serializer.instance.save()
#         subject = 'New Article Added'
#         details = "\n                ".join([f"{key}: {value}" for key, value in serializer.data.items()])
#         message = f"""User Details:
#                         User ID: {user_id}
#                         First Name: {user.surname}
#                         Last Name: {user.full_name}
#                         Contact Number: {user.contact_number}
#                     Details:
#                         {details}
#         """

#         recipient_email = 'sathayushtechsolutions@gmail.com'  # replace with your email
#         self.send_email(recipient_email, subject, message)
#         return Response({
#             "message": "success",
#             "result": serializer.data
#         })


# class EditArticle(generics.GenericAPIView):
#     serializer_class = ArticleSerializer
     
    
#     def is_email(self, username):
#         return re.match(r"[^@]+@gmail\.com$", username)

#     def send_email(self, email, subject, message):
#         from_email = settings.EMAIL_HOST_USER
#         recipient_list = [email]
#         try:
#             send_mail(subject, message, from_email, recipient_list)
#             print("Email sent successfully")
#         except Exception as e:
#             print(f"Failed to send email: {e}")

#     def get_user_details(self, user_id):
#         try:
#             user = Register.objects.get(id=user_id)
#             return {
#                 "user_id": user.id,
#                 "surname": user.surname,
#                 "full_name": user.full_name,
#                 "contact_number": user.contact_number,
#             }
#         except Register.DoesNotExist:
#             return None

#     def put(self, request, _id):
#         user_id = request.data.get('user')
#         if not user_id:
#             return Response({"error": "User ID is required"}, status=400)
        
#         user_details = self.get_user_details(user_id)
#         if not user_details:
#             return Response({"error": "User not found"}, status=404)

#         # Retrieve the instance
#         instance = get_object_or_404(ArticleModel, _id=_id)
#         pdf_location = request.data.get('pdf_location')
#         mutable_data = request.data.copy()
#         mutable_data['pdf_location'] = "null"
#         serializer = self.get_serializer(instance, data=mutable_data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         if pdf_location and pdf_location != "null":
#             saved_location = save_pdf_to_azure(pdf_location, serializer.instance._id, serializer.instance.category_id.name, "article")
#             if saved_location:
#                 serializer.instance.pdf_location = saved_location
#                 serializer.instance.save()

#         # Update NewsCategory
#         instance_news = get_object_or_404(ArticleModel, _id=_id)
#         image_location = request.data.get('image_location')
#         mutable_data_news = request.data.copy()
#         mutable_data_news['image_location'] = "image_location"
#         serializer_news = self.get_serializer(instance_news, data=mutable_data_news)
#         serializer_news.is_valid(raise_exception=True)
#         serializer_news.save()

#         if image_location and image_location != "null":
#             saved_image_location = save_image_to_azure(image_location, serializer.instance._id, serializer.instance.category_id.name, "article")
#             if saved_image_location:
#                 serializer.instance.image_location = saved_image_location
#                 serializer.instance.save()
#         subject = 'Edit Article Added'
#         message = f"""User Details:
#         User ID: {user_details['user_id']}
#         First Name: {user_details['surname']}
#         Last Name: {user_details['full_name']}
#         Contact Number: {user_details['contact_number']}
#         Details: {serializer.data}
#         """
#         recipient_email = 'sathayushtechsolutions@gmail.com'  # replace with your email
#         self.send_email(recipient_email, subject, message)

#         return Response({
#             "message": "success",
#             "result": serializer.data
#         })

    
# class GetArticlesByDateView(APIView):
#     serializer_class = ArticleSerializer1
#     pagination_class = ArticlesCustomPagination

#     def get(self, request, *args, **kwargs):
  
#         queryset = ArticleModel.objects.filter(status='SUCCESS').order_by('-created_at')



#         _id = request.query_params.get('_id')
#         author = request.query_params.get('author')
#         created_at = request.query_params.get('created_at')
#         date = request.query_params.get('date')
#         article_user= request.query_params.get('article_user')
#         category_id = request.query_params.get('category_id')
#         article_user_name = request.query_params.get('article_user_name')

#         if article_user_name:
#             queryset = queryset.filter(article_user__name=article_user_name)

        
#         if article_user:
#             queryset = queryset.filter(article_user=article_user)

#         if category_id:
#             queryset = queryset.filter(category_id=category_id)

#         if _id:
#             queryset = queryset.filter(_id=_id)
#         if author:
#             queryset = queryset.filter(author=author)
#         if date:
#             queryset = queryset.filter(date=date)


#         # Filter by news_sub_category_id if provided
       
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
#         paginator = ArticlesCustomPagination()
#         paginated_queryset = paginator.paginate_queryset(queryset, request)
#         serializer = ArticleSerializer1(paginated_queryset, many=True)
#         return paginator.get_paginated_response(serializer.data)



# # class LatestArticleNewsView(generics.ListAPIView):
# #     serializer_class = ArticleSerializer1

# #     def get(self, request, *args, **kwargs):
# #         result = {}
# #         articles = ArticleModel.objects.filter(status='SUCCESS').order_by('-created_at')[:5]  # Fetch the latest article

# #         serializer = self.get_serializer(articles, many=True)
# #         result["latest_articles"] = serializer.data
        
# #         response_data = {
# #             # "status": "success",
# #             "result": result
# #         }
# #         return Response(response_data)

# class LatestArticleNewsView(generics.ListAPIView):
#     serializer_class = ArticleSerializer1

#     def get(self, request, *args, **kwargs):
#         result = {}
#         # Fetch all articles with status 'SUCCESS', ordered by 'created_at' in descending order
#         articles = ArticleModel.objects.filter(status='SUCCESS').order_by('-created_at')[:30]

#         serializer = self.get_serializer(articles, many=True)
#         result["latest_articles"] = serializer.data
        
#         response_data = {
#             # "status": "success",
#             "result": result
#         }
#         return Response(response_data)

#------------------latest articles ---------------------------

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import OuterRef, Subquery
from django.utils import timezone
from ..models import ArticleModel
from ..serializers import ArticleSerializer1
from ..enums import EntityStatus, IsPublish
class LatestArticlePerCategoryAPIView(APIView):
    def get(self, request):
        latest_article_subquery = (
            ArticleModel.objects
            .filter(
                category_id=OuterRef("category_id"),status='SUCCESS',
            )
            .order_by("-created_at")
            .values("_id")[:1]
        )
        articles = (
            ArticleModel.objects
            .filter(_id=Subquery(latest_article_subquery))
            .select_related("category_id", "article_user")
        )
        serializer = ArticleSerializer1(articles, many=True)
        return Response(serializer.data)