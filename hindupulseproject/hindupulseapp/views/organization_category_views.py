from rest_framework import viewsets
from ..models import OrganizationCategory
from ..serializers import OrganizationCategorySerializer
from ..pagination import CustomPagination 
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.views import APIView
from rest_framework import status





class OrganizationCategoryViewSet(viewsets.ModelViewSet):
    queryset = OrganizationCategory.objects.all()
    serializer_class = OrganizationCategorySerializer
    pagination_class = CustomPagination

 
    

class GetOrganizationCategoryById_InputView(APIView):
    #serializer_class = NewsSubCategorySerializer

    def get(self, request, _id):
        try:
           
            field_names = [field.name for field in OrganizationCategory._meta.get_fields()]
            print(field_names, "Available field names")
         
            filter_kwargs = {"other_category": _id}
            print(filter_kwargs, "Filter arguments")

           
            queryset = OrganizationCategory.objects.filter(**filter_kwargs)
          
            paginator = CustomPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            
            
            serialized_data = OrganizationCategorySerializer(paginated_queryset, many = True)
            return paginator.get_paginated_response(serialized_data.data)
        
        except OrganizationCategory.DoesNotExist:
            return Response({
                'message': 'Object not found',
                'status': 404
            }, status=status.HTTP_404_NOT_FOUND)





