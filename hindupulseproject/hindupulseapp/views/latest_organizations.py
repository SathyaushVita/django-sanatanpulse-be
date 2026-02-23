
from rest_framework import generics
from rest_framework.response import Response
from ..models import OrganizationCategory, Organizations
from ..serializers import OrganizationsSerializer1


class LatestOrganizationsView(generics.ListAPIView):
    serializer_class = OrganizationsSerializer1

    def get(self, request, *args, **kwargs):
        result = {}
        # Retrieve all categories
        categories = OrganizationCategory.objects.all()  # Order categories by priority_order if needed

        # Iterate over each category and get related organizations
        for category in categories:
            # Query Organizations model for items with the current category and SUCCESS status
            news_items = Organizations.objects.filter(organization_category=category, status='SUCCESS').order_by('priority_order')
            
            # Serialize the data
            serializer = self.get_serializer(news_items, many=True)
            result[category.name] = serializer.data
        
        response_data = {"result": result}
        return Response(response_data)
