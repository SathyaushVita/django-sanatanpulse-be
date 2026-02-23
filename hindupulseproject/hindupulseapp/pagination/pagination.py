#from rest_framework.pagination import PageNumberPagination

#class CustomPagination(PageNumberPagination):
#    page_size = 50
#    page_size_query_param = 'page_size'
#    max_page_size = 100


# from rest_framework.pagination import PageNumberPagination

# class CustomPagination(PageNumberPagination):
#     page_size = 5
#     page_size_query_param = 'page_size'
#     max_page_size = 100

    

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,  # Total items
            'total_pages': self.page.paginator.num_pages,  # Total pages
            'next': self.get_next_link(),  # URL for the next page
            'previous': self.get_previous_link(),  # URL for the previous page
            'results': data,  # Paginated data
        })

