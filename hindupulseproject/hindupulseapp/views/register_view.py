from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from ..models import Register,ArticleModel,NewsCategory
from ..utils import save_image_to_azure,image_path_to_binary
from ..serializers import LoginSerializer, VerifySerializer, ResendOtpSerializer
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
from ..serializers import MoreDetailsSerializer,NewsCategorySerializer1,ArticleSerializer1
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
import base64
# from ..enums.member_visibility_enum import MemberVisibility

from django.db.models import Q  # Import Q for complex queries

sms_user = settings.SMS_USER
sms_password = settings.SMS_PASSWORD
sms_sender = settings.SMS_SENDER
sms_type = settings.SMS_TYPE
sms_template_id = settings.SMS_TEMPLATE_ID
RESEND_SMS = settings.RE_SMS_TEMPLATE_ID





class GetProfile(APIView):
    def get(self, request):
        queryset = Register.objects.all()
        response_data = []

        print(f"Total profiles found: {queryset.count()}")  # Debug statement
        
        for item in queryset:
            item_data = MoreDetailsSerializer(item).data
            profile_pic_path = item.profile_pic
            print(f"Processing profile: {item.id}")  # Debug statement
            
            if profile_pic_path:
                try:
                    # Since the profile_pic URL is already correct, just use it as is
                    item_data['profile_pic'] = profile_pic_path
                except Exception as e:
                    print(f"Error handling profile picture for {item.id}: {e}")  # Debug statement
                    item_data['profile_pic'] = None
            else:
                print(f"No profile picture for profile: {item.id}")  # Debug statement
                item_data['profile_pic'] = None
            
            response_data.append(item_data)
        
        print(f"Total profiles added to response: {len(response_data)}")  # Debug statement
        
        return Response(response_data, status=status.HTTP_200_OK)




class GetProfileById(APIView):
    def get(self, request, id):
        queryset = Register.objects.filter(id=id)
        response_data = []

        if not queryset.exists():
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        print(f"Total profiles found: {queryset.count()}")  # Debug statement
        
        for item in queryset:
            item_data = MoreDetailsSerializer(item).data
            profile_pic_path = item.profile_pic
            print(f"Processing profile: {item.id}")  # Debug statement
            
            if profile_pic_path:
                try:
                    # Assuming `image_path_to_binary` is a utility function to convert image to binary/base64
                    encoded_string = image_path_to_binary(profile_pic_path)
                    if encoded_string:
                        item_data['profile_pic'] = encoded_string
                    else:
                        print(f"Encoding failed for profile: {item.id}")  # Debug statement
                        item_data['profile_pic'] = None
                except Exception as e:
                    print(f"Error encoding profile picture for {item.id}: {e}")  # Debug statement
                    item_data['profile_pic'] = None
            else:
                print(f"No profile picture for profile: {item.id}")  # Debug statement
                item_data['profile_pic'] = None  # Set to None if profile picture is not present

            # Fetch user's news
            news_queryset = NewsCategory.objects.filter(user=item)
            news_data = NewsCategorySerializer1(news_queryset, many=True).data
            item_data['news'] = news_data

            # Fetch user's articles
            article_queryset = ArticleModel.objects.filter(user=item)  # Use item.id or adjust based on model
            article_data = ArticleSerializer1(article_queryset, many=True).data
            item_data['articles'] = article_data
            
            response_data.append(item_data)
        
        print(f"Total profiles added to response: {len(response_data)}")  # Debug statement
        
        return Response(response_data, status=status.HTTP_200_OK)


   

class ProfileUpdate(generics.GenericAPIView):
    serializer_class = MoreDetailsSerializer
    
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
        instance = get_object_or_404(Register, id=id)
        
        # Retrieve the new email and contact number from the request data
        new_email = request.data.get('email')
        new_contact_number = request.data.get('contact_number')
        # new_username = request.data.get('username') 
        
        # Check if email or contact number already exists for another user
        if Register.objects.filter(email=new_email).exclude(id=id).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        if Register.objects.filter(contact_number=new_contact_number).exclude(id=id).exists():
            return Response({"error": "Contact number already exists"}, status=status.HTTP_400_BAD_REQUEST)
        #check with the username
        # if Register.objects.filter(username=new_contact_number).exclude(id=id).exists():
        #     return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        # if Register.objects.filter(username=new_email).exclude(id=id).exists():
        #     return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
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
            saved_location = save_image_to_azure(profile_pic, serializer.instance.id, serializer.instance.full_name, "profile_pic")
            if saved_location:
                serializer.instance.profile_pic = saved_location
                print(serializer.instance.profile_pic, "referg")
                serializer.instance.save()
        else:
            # Set profile_pic to None if it’s not provided or is "null"
            serializer.instance.profile_pic = None

        # Send email with the required information
        subject = 'Profile Updated'
        message = 'REGISTRATION SUCCESSFUL, Now you are connected to our four websites. Thanks for being a part of Hindu Pulse!'
        recipient_email = 'sathayushtechsolutions@gmail.com'  
        self.send_email(recipient_email, subject, message)

        # Prepare the response with profile_pic as None if not provided
        response_data = serializer.data
        response_data['profile_pic'] = serializer.instance.profile_pic or None

        return Response({
            "message": "Profile updated successfully",
            "result": response_data
        })





class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    FIXED_OTP_USERS = {
        'contact_numbers': ['7680822565'],  # Replace with your fixed contact numbers
        'emails': ['sathayushtechsolutions@gmail.com']  # Replace with your fixed email addresses
    }

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data.get('username')

        if not username:
            return Response({"error": "username is required"}, status=status.HTTP_400_BAD_REQUEST)

        is_email = self.is_email(username)
        email = username if is_email else None
        contact_number = username if not is_email else None

        # Determine if this is a fixed OTP user
        fixed_otp = None
        if email in self.FIXED_OTP_USERS['emails'] or contact_number in self.FIXED_OTP_USERS['contact_numbers']:
            fixed_otp = '0000'

        # Check if the user exists by either email or contact number
        user = self.get_user_by_email_or_contact(email, contact_number)

        if user:
            # User exists, set OTP
            user.verification_otp = fixed_otp if fixed_otp else self.generate_otp()
            user.verification_otp_created_time = timezone.now()
            user.save(using='user_db')
            message = "Login successful and OTP sent successfully"
        else:
            # Create a new user if they don't exist
            user = Register.objects.using('user_db').create(
                username=username,
                email=email,
                contact_number=contact_number,
                verification_otp=fixed_otp if fixed_otp else self.generate_otp(),
                verification_otp_created_time=timezone.now()
            )
            user.save(using='user_db')
            message = "OTP sent successfully"

        otp_new = user.verification_otp

        # Send OTP via email or SMS based on the input type
        if is_email:
            validation_error = self.send_email(email, otp_new)
            if validation_error:
                return Response({"error": validation_error}, status=status.HTTP_400_BAD_REQUEST)
        else:
            validation_error = self.validate_phone_number(contact_number)
            if validation_error:
                return Response({"error": validation_error}, status=status.HTTP_400_BAD_REQUEST)
            self.send_sms(contact_number, otp_new)

        return Response({"message": message}, status=status.HTTP_200_OK)


    def get_user_by_email_or_contact(self, email, contact_number):
        """
        Check if a user exists by either email or contact number.
        """
        try:
            if email:
                users = Register.objects.using('user_db').filter(email=email)
            elif contact_number:
                users = Register.objects.using('user_db').filter(contact_number=contact_number)
            
            if users.exists():
                return users.first()  # If multiple users exist, return the first one
            else:
                return None
        except Exception as e:
            print(f"Error retrieving user: {e}")
            return None

    def generate_otp(self):
        import random
        return str(random.randint(1000, 9999))

    def is_email(self, username):
     return re.match(r"[^@]+@(gmail\.com|yahoo\.com|echina\.com)$", username)


    def validate_phone_number(self, phone_number):
        if not re.match(r"^\d{10}$", phone_number):
            return "Invalid username format. Must be either a valid email or a 10-digit phone number."
        return None

    def send_sms(self, username, otp):
        url = (
            f"http://api.bulksmsgateway.in/sendmessage.php?user={sms_user}&password={sms_password}&mobile={username}&message="
            f"Dear user your OTP to verify your Gramadevata User account is {otp}. Thank You! team Sathayush.&sender={sms_sender}&type={sms_type}&template_id={sms_template_id}"
        )
        response = requests.get(url)
        print(response.text)
        print("Sent Mobile OTP")

    def send_email(self, email, otp):
        subject = "Your OTP Code"
        message = f"Dear user, your OTP to verify your Hindupulse User account is {otp}. Thank You! team Sathayush."
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        try:
            send_mail(subject, message, from_email, recipient_list)
            print("Sent Email OTP")
            return None
        except Exception as e:
            print(f"Failed to send email: {e}")
            return "Failed to send OTP email."
        


from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.db.models import Q

from ..models import Register
from ..serializers import VerifySerializer


# class ValidateOTPView(generics.GenericAPIView):
#     serializer_class = VerifySerializer

#     def post(self, request, *args, **kwargs):
#         username = request.data.get('username')
#         verification_otp = request.data.get('verification_otp')
        
#         try:
#             # 🔍 Find user by email / contact / username
#             user = Register.objects.using('user_db').filter(
#                 Q(username=username) |
#                 Q(contact_number=username) |
#                 Q(email=username),
#                 verification_otp=verification_otp
#             ).first()
            
#             if not user:
#                 return Response(
#                     {'error': 'Invalid credentials'},
#                     status=status.HTTP_401_UNAUTHORIZED
#                 )

#             # ⏰ OTP expiry check
#             if user.verification_otp_created_time < timezone.now() - timezone.timedelta(hours=24):
#                 return Response(
#                     {"error": "OTP expired"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
                
#             # ✅ Activate user
#             user.status = 'ACTIVE'
#             user.save(using='user_db')
                
#             # 🔐 JWT TOKEN GENERATION (SSO ENABLED) 🔥
#             refresh = RefreshToken.for_user(user)
#             access = refresh.access_token

#             # 🔑 COMMON SSO PAYLOAD (🔥 NEW)
#             access['user_id'] = user.id
#             access['username'] = user.username
#             access['email'] = user.email
#             access['contact_number'] = user.contact_number
#             access['source'] = 'sanatana'   # 🔴 IMPORTANT

#             return Response({
#                 'refresh': str(refresh),
#                 'access': str(access),
#                 'sso_token': str(access),   # 🔥 NEW (USED FOR AUTO LOGIN)
#                 'username': user.get_username(),
#                 'user_id': user.id,
#                 "is_member": user.is_member,
#                 "profile_pic": user.profile_pic,
#                 "surname": user.surname,
#                 "full_name": user.full_name,
#             }, status=status.HTTP_200_OK)
        
#         except Exception as e:
#             return Response(
#                 {"error": "Invalid credentials"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )




class ValidateOTPView(generics.GenericAPIView):
    serializer_class = VerifySerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        verification_otp = request.data.get('verification_otp')
        
        try:
            # Find user by either email or contact number with the provided OTP
            user = Register.objects.using('user_db').filter(
                Q(username=username) | Q(contact_number=username)| Q(email=username), 
                verification_otp=verification_otp
            ).first()
            
            if user:
                # Check if the OTP is still valid (within 24 hours)
                if user.verification_otp_created_time < timezone.now() - timezone.timedelta(hours=24):
                    return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Set user status to ACTIVE
                user.status = 'ACTIVE'
                user.save(using='user_db')
                
                # Generate JWT token pair
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'username': user.get_username(),
                    'user_id': user.id,
                    "is_member": user.is_member,
                    "profile_pic": user.profile_pic,
                    "surname": user.surname,
                    "full_name": user.full_name,

                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials', 'status': '401'}, status=status.HTTP_401_UNAUTHORIZED)
        
        except Register.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        

        
class ResendOTPView(generics.GenericAPIView):
    serializer_class = ResendOtpSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        if not username:
            return Response({"error": "username is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            otp = Register.objects.using('user_db').get(username=username)
            otp.generate_verification_otp()
            otp_new = otp.verification_otp
            if self.is_email(username):
                LoginView().send_email(username, otp_new)
            else:
                LoginView().send_sms(username, otp_new)
            return Response({"otp": "otp sent successfully"}, status=status.HTTP_200_OK)
        except Register.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def is_email(self, username):
        return re.match(r"[^@]+@gmail\.com$", username)





