

from rest_framework import serializers
from ..models import Register
from ..utils import image_path_to_binary

class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
  
    class Meta:
        model = Register
       
        fields = ["username"]
     
        
class VerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Register
        fields =["username","verification_otp"]


class ResendOtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Register
        fields =["username"]


class MoreDetailsSerializer(serializers.ModelSerializer):
 
    class Meta:
        model=Register
        # fields=["id","full_name","father_name","profile_pic","contact_number","gender"]
        fields=["id","surname","full_name","father_name","email","profile_pic","contact_number","gender"]
     
      
