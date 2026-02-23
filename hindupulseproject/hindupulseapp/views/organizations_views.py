from rest_framework import viewsets
from ..models import *
from ..serializers import *
from rest_framework.views import *
from rest_framework import generics
# from ..utils import save_image_to_folder
from ..utils import save_image_to_azure
from django.shortcuts import get_object_or_404
from ..pagination.pagination import CustomPagination 
from django.db.models import Q


class OrganizationsViewSet(viewsets.ModelViewSet):
    queryset = Organizations.objects.filter(status='SUCCESS').order_by('name')
    serializer_class = OrganizationsSerializer1

class OrganizationsPost(generics.GenericAPIView):
    serializer_class = OrganizationsSerializer
    
   
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
            "message": "Organizations Added successfully",
            "result": serializer.data
        })
    

class OrganizationsUpdate(generics.GenericAPIView):
    serializer_class = OrganizationsSerializer
    
    
    def put(self, request, _id):
        # Retrieve the instance
        instance = get_object_or_404(Organizations, _id=_id)
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
            "message": "Organizations updated successfully",
            "result": serializer.data
        })
    

  
class Organization_GetItemByfield_InputView(APIView):
    serializer_class = OrganizationsSerializer1
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        queryset = Organizations.objects.filter(status='SUCCESS').order_by('-created_at')
      
        organization_category = request.query_params.get('organization_category')
      
        # Filter by news_sub_category_id if provided
        if organization_category:
            queryset = queryset.filter(organization_category=organization_category)
      

        # Pagination
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = OrganizationsSerializer1(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

