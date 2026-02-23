from rest_framework import generics
from rest_framework.response import Response
from ..models import NewsCategory, Category
from ..serializers import NewsCategorySerializer1
from django.db.models import Max
from rest_framework import generics, status

class LatestNewsView(generics.ListAPIView):
    serializer_class = NewsCategorySerializer1

    def get(self, request, *args, **kwargs):
        result = {}
        categories = Category.objects.all().order_by('priority_order')  # Order categories by priority_order
        # today = date.today()

        for category in categories:
            if category.name.lower() == 'outlook':  # Check if category is "Outlook"
                news_items = NewsCategory.objects.filter(
                    category_id=category,
                    status='SUCCESS',
                    is_published='PUBLISHED'
                ).order_by('-created_at')
            else:
                news_items = NewsCategory.objects.filter(
                    category_id=category,
                    status='SUCCESS',
                    is_published='PUBLISHED'
                ).order_by('-created_at')[:2]  # Fetch the 2 latest news items

            serializer = self.get_serializer(news_items, many=True)
            result[category.name] = serializer.data

        response_data = {"result": result}
        return Response(response_data)


# class LatestNewsByStateView(generics.ListAPIView):
#     serializer_class = NewsCategorySerializer1

#     def get_queryset(self):
#         # List of states
#         states = [
#             "Andhra Pradesh", "Bihar&Jharkhand", "Chhattisgarh", "Delhi",
#             "Gujarat", "Himachal Pradesh", "Haryana", "Jammu And Kashmir", "Kerala",
#             "Karnataka", "Madhya Pradesh", "Maharashtra&Goa", "Odisha",
#             "Punjab", "Rajasthan", "Telangana", "Tamil Nadu", "Uttar Pradesh",
#             "West Bengal", "Uttarakhand", "North East States",
#         ]

#         # Get the latest news for each state
#         latest_news = NewsCategory.objects.filter(
#             location__in=states, status='SUCCESS'
#         ).values('location').annotate(latest_created_at=Max('created_at')).order_by('location')

#         # Now, for each state, fetch the corresponding latest news record
#         news_records = []
#         for state in latest_news:
#             news_record = NewsCategory.objects.filter(
#                 location=state['location'], created_at=state['latest_created_at']
#             ).first()
#             if news_record:
#                 news_records.append(news_record)

#         return news_records

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)






class LatestNewsByStateView(generics.ListAPIView):
    serializer_class = NewsCategorySerializer1

    def get_states(self):
        """Return a list of predefined states and groups (total 24)."""
        state_groups = {
            "Bihar": ["Bihar", "Jharkhand"],
            "Maharashtra": ["Maharashtra", "Goa"],
            "Andhra Pradesh": ["Andhra Pradesh"], 
            "Bihar": ["Bihar"],
            "Jharkhand": ["Jharkhand"],
            "Maharashtra": ["Maharashtra"],
            "Goa": ["Goa"],
            "Andhra Pradesh": ["Andhra Pradesh"],
            "Bihar": ["Bihar"],
            "Jharkhand": ["Jharkhand"],
            "Maharashtra": ["Maharashtra"],
            "Goa": ["Goa"],
            "Chhattisgarh": ["Chhattisgarh"],
            "Delhi": ["Delhi"],
            "Gujarat": ["Gujarat"],
            "Himachal Pradesh": ["Himachal Pradesh"],
            "Haryana": ["Haryana"],
            "Jammu and Kashmir and Ladakh": ["Jammu And Kashmir", "Ladakh"],
            "Kerala": ["Kerala"],
            "Karnataka": ["Karnataka"],
            "Madhya Pradesh": ["Madhya Pradesh"],
            "Odisha": ["Odisha"],
            "Punjab and Chandigarh": ["Punjab", "Chandigarh"],
            "Rajasthan": ["Rajasthan"],
            "Telangana": ["Telangana"],
            "Tamil Nadu": ["Tamil Nadu"],
            "Uttar Pradesh": ["Uttar Pradesh"],
            "West Bengal": ["West Bengal"],
            "Uttarakhand": ["Uttarakhand"],
            "North East States": [
                "Assam", "Nagaland", "Manipur", "Tripura", "Mizoram", "Arunachal Pradesh", "Meghalaya", "Sikkim"
            ],
            "Union Territories": [
                "Puducherry", "Andaman and Nicobar Islands","Dadra and Nagar Haveli and Daman and Diu","Lakshadweep",
            ]
        }

        return list(state_groups.values())

    def get_queryset(self):
        """Get the latest news for each state or group."""
        state_groups = self.get_states()
        latest_news_records = []

        for group in state_groups:
            latest_news = NewsCategory.objects.filter(
                location__in=group, status='SUCCESS', is_published='PUBLISHED'
            ).order_by('-created_at').first()  # Fetch the most recent news for the group
            
            if latest_news:
                latest_news_records.append(latest_news)

        return latest_news_records

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)







# class LatestNewsByStateView(generics.ListAPIView):
#     serializer_class = NewsCategorySerializer1

#     def get_states(self):
#         """Return a flattened list of states."""
#         states = [
#             "Andhra Pradesh", "Bihar","Jharkhand", "Chhattisgarh", "Delhi",
#             "Gujarat", "Himachal Pradesh", "Haryana", "Jammu And Kashmir", "Kerala",
#             "Karnataka", "Madhya Pradesh", "Maharashtra","Goa", "Odisha",
#             "Punjab", "Rajasthan", "Telangana", "Tamil Nadu", "Uttar Pradesh",
#             "West Bengal", "Uttarakhand", "North East States",
#         ]

#         # Flatten states with '&'
#         flattened_states = []
#         for state in states:
#             if "&" in state:
#                 flattened_states.extend(state.split("&"))
#             else:
#                 flattened_states.append(state)
#         return flattened_states

#     def get_queryset(self):
#         """Get the latest news for each state."""
#         states = self.get_states()

#         # Annotate with the latest created_at for each state
#         latest_news = NewsCategory.objects.filter(
#             location__in=states, status='SUCCESS'
#         ).values('location').annotate(latest_created_at=Max('created_at')).order_by('location')

#         # Fetch the latest news record for each state
#         news_records = []
#         for state in latest_news:
#             news_record = NewsCategory.objects.filter(
#                 location=state['location'], created_at=state['latest_created_at']
#             ).first()
#             if news_record:
#                 news_records.append(news_record)

#         return news_records

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)










# from datetime import datetime, timedelta
# from django.utils.timezone import make_aware

# class LatestNewsHomeView(generics.ListAPIView):
#     serializer_class = NewsCategorySerializer1

#     def get(self, request, *args, **kwargs):

#         # ---- TODAY & YESTERDAY RANGE ----
#         today = datetime.today().date()
#         yesterday = today - timedelta(days=1)

#         start_datetime = make_aware(datetime.combine(yesterday, datetime.min.time()))
#         end_datetime = make_aware(datetime.combine(today, datetime.max.time()))

#         # ---- GET ONLY TODAY + YESTERDAY NEWS (LIMIT 12) ----
#         news_items = NewsCategory.objects.filter(
#             status='SUCCESS',
#             is_published='PUBLISHED',
#             created_at__range=[start_datetime, end_datetime]
#         ).order_by('-created_at')[:12]

#         serializer = self.get_serializer(news_items, many=True)

#         return Response({"result": serializer.data})




from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from rest_framework import generics
from rest_framework.response import Response

class LatestNewsHomeView(generics.ListAPIView):
    serializer_class = NewsCategorySerializer1

    def get(self, request, *args, **kwargs):

        today = datetime.today().date()
        yesterday = today - timedelta(days=1)

        start_datetime = make_aware(datetime.combine(yesterday, datetime.min.time()))
        end_datetime = make_aware(datetime.combine(today, datetime.max.time()))

        # ---- TRY LAST 2 DAYS NEWS (LIMIT 10) ----
        news_items = NewsCategory.objects.filter(
            status='SUCCESS',
            is_published='PUBLISHED',
            created_at__range=[start_datetime, end_datetime]
        ).order_by('-created_at')[:10]

        # ---- IF NO NEWS FOUND, FETCH LATEST OLD NEWS (LIMIT 10) ----
        if not news_items.exists():
            news_items = NewsCategory.objects.filter(
                status='SUCCESS',
                is_published='PUBLISHED'
            ).order_by('-created_at')[:10]

        serializer = self.get_serializer(news_items, many=True)
        return Response({"result": serializer.data})
