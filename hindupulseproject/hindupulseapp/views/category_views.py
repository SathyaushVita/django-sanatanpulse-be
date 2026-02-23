from rest_framework import viewsets
from ..models import *
from ..serializers import *
from rest_framework.views import *


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('priority_order')
    serializer_class = CategorySerializer


from rest_framework import viewsets
from rest_framework.response import Response
from ..models import Category
from ..serializers import CategorySerializer1

class CategoryViewSet1(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer1


class Category_GetItemByfield_InputView(APIView):
    # serializer_class = NewsCategorySerializer

    def get(self, request, input_value, field_name):
        try:
           
            field_names = [field.name for field in Category._meta.get_fields()]

            
            if field_name in field_names:
               
                filter_kwargs = {field_name: input_value}
                newsdata = Category.objects.filter(**filter_kwargs)
               
                serialized_data = CategorySerializer(newsdata, many=True)

                return Response(serialized_data.data)
                
              
            else:
                return Response({
                    'message': 'Invalid field name',
                    'status': 400
                })

        except Category.DoesNotExist:
            return Response({
                'message': 'Object not found',
                'status': 404
            })


