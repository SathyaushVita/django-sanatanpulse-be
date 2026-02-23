from rest_framework import viewsets
from ..models import Media
from ..serializers import MediaSerializer,MediaSerializer1
from rest_framework import generics
from ..utils import save_image_to_azure_v2
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from rest_framework.views import APIView
from ..pagination.pagination import CustomPagination 
from django.db.models import Q

class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.filter(status='SUCCESS')
    serializer_class = MediaSerializer1


class AddMediaView(generics.GenericAPIView):
    serializer_class = MediaSerializer
   
    def post(self, request, *args, **kwargs):
      
      
        image_location = request.data.get('image_location', [])
        if not isinstance(image_location, list):
            return JsonResponse({"error": "Image location must be a list"}, status=400)

        # Make a mutable copy of request.data
        mutable_data = request.data.copy()
        mutable_data['image_location'] = []
        


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

      

    
        return Response({
            "message": "success",
            "result": serializer.data
        })
    




class EditMedia(generics.GenericAPIView):
    serializer_class = MediaSerializer

   
    def put(self, request, _id):
     

        # Retrieve the instance
        instance = get_object_or_404(Media, _id=_id)


        # Retrieve image_location from request data
        image_location = request.data.get('image_location', [])
        if not isinstance(image_location, list):
            return JsonResponse({"error": "Image location must be a list"}, status=400)

        # Make a mutable copy of request.data
        mutable_data = request.data.copy()
        mutable_data['image_location'] = instance.image_location  # Preserve existing image locations
      

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

      
     
        # Send email with the required information
      
        return Response({
            "message": "success",
            "result": serializer.data
        })


class Media_GetItemByfield_InputView(APIView):
    serializer_class = MediaSerializer1
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        queryset = Media.objects.filter(status='SUCCESS').order_by('-created_at')
        # queryset = NewsCategory.objects.filter(status='SUCCESS',is_published='PUBLISHED').order_by('-created_at')
        # queryset = NewsCategory.objects.filter(status='SUCCESS', publish_at__lte=timezone.now()).order_by('-publish_at')

        other_category = request.query_params.get('other_category')
        # news_sub_category_id = request.query_params.get('news_sub_category_id')
        # created_at = request.query_params.get('created_at')
        # language = request.query_params.get('language')

        # Filter by category_id if provided
       

        # Filter by news_sub_category_id if provided
        if other_category:
            queryset = queryset.filter(other_category=other_category)
        # if language:
        #     queryset = queryset.filter(language=language)

        

        # Pagination
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = MediaSerializer1(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)