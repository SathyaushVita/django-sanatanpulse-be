from rest_framework import viewsets
from ..models import *
from ..serializers import *
from rest_framework.views import *
from rest_framework import generics
# from ..utils import save_image_to_folder
from ..utils import save_image_to_azure
from django.shortcuts import get_object_or_404


class ArticleCategoryViewSet(viewsets.ModelViewSet):
    queryset = ArticleCategory.objects.all().order_by('name')
    serializer_class = ArticleCategorySerializer1

class ArticleCategoryPost(generics.GenericAPIView):
    serializer_class = ArticleCategorySerializer
    
   
    def post(self, request, *args, **kwargs):
        # Retrieve profile_pic from request data
        profile_pic = request.data.get('profile_pic')
        # print(profile_pic, "vfvfv")

        # Instantiate the serializer with request data
        serializer = self.get_serializer(data=request.data)
        print("dddddddddd", serializer)
        serializer.is_valid(raise_exception=True)
        # serializer.validated_data['is_member'] = "YES"
        serializer.save()

        # If profile_pic is provided and not "null", save the image
        if profile_pic and profile_pic != "null":
            saved_location = save_image_to_azure(profile_pic, serializer.instance._id, serializer.instance.name, "article")
            if saved_location:
                serializer.instance.profile_pic = saved_location
                print(serializer.instance.profile_pic, "referg")
                serializer.instance.save()

        # Send email with the required information
       

        return Response({
            "message": "Profile Added successfully",
            "result": serializer.data
        })
    

class UpdateArticleCategory(generics.GenericAPIView):
    serializer_class = ArticleCategorySerializer
    
    
    def put(self, request, _id):
        # Retrieve the instance
        instance = get_object_or_404(ArticleCategory, _id=_id)
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
        # serializer.validated_data['is_member'] = "YES"
        serializer.save()
        
        # If profile_pic is provided and not "null", save the image
        if profile_pic and profile_pic != "null":
            saved_location = save_image_to_azure(profile_pic, serializer.instance._id, serializer.instance.name,"article")
            if saved_location:
                serializer.instance.profile_pic = saved_location
                print(serializer.instance.profile_pic, "referg")
                serializer.instance.save()
        
      

        return Response({
            "message": "Profile updated successfully",
            "result": serializer.data
        })