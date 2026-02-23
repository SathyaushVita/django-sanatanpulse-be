

from rest_framework import viewsets
from ..models import OutlookCommentModel
from ..serializers import Outlook_CommentSerializer,Outlook_CommentSerializer1
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.utils.timesince import timesince
from ..pagination import CustomPagination
from ..enums.is_reply_enum import IsReplyEnum
from ..enums.member_status_enum import MemberStatus
# class CommentView(viewsets.ModelViewSet):
#     queryset = NewsCommentModel.objects.filter(is_reply=IsReplyEnum.NO.value)  # Filter out replies
#     serializer_class = CommentSerializer1  # Default serializer class for create

#     def get_serializer_class(self):
#         if self.action == 'list':
#             return CommentSerializer
#         return self.serializer_class

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         parent_id = serializer.validated_data.get('parent')
#         if parent_id is not None:
#             serializer.validated_data['is_reply'] = IsReplyEnum.YES.value
#         else:
#             serializer.validated_data['is_reply'] = IsReplyEnum.NO.value

#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

#     def list(self, request, *args, **kwargs):
#         queryset = NewsCommentModel.objects.filter(is_reply=IsReplyEnum.NO.value).order_by('-created_at')
#         for comment in queryset:
#             if comment.created_at:
#                 comment.posted_time_ago = f"{timesince(comment.created_at)} ago"
#                 comment.save()
#         return super().list(request, *args, **kwargs)



class Outlook_CommentView(viewsets.ModelViewSet):
    queryset = OutlookCommentModel.objects.filter(is_reply=IsReplyEnum.NO.value)  # Filter out replies
    serializer_class = Outlook_CommentSerializer1  # Default serializer class for create

    def get_serializer_class(self):
        if self.action == 'list':
            return Outlook_CommentSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        user = request.user  # Get the user from the request
        
        # Check if the user is authenticated
        if not user.is_authenticated:
            return Response(
                {"error": "Authentication credentials were not provided."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if the user is a member
        if user.is_member == MemberStatus.false.value:  
            return Response(
                {"error": "user is not a member"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        parent_id = serializer.validated_data.get('parent')
        if parent_id is not None:
            serializer.validated_data['is_reply'] = IsReplyEnum.YES.value
        else:
            serializer.validated_data['is_reply'] = IsReplyEnum.NO.value

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = OutlookCommentModel.objects.filter(is_reply=IsReplyEnum.NO.value).order_by('-created_at')
        for comment in queryset:
            if comment.created_at:
                comment.posted_time_ago = f"{timesince(comment.created_at)} ago"
                comment.save()
        return super().list(request, *args, **kwargs)

class Outlook_GetCommentById_InputView(APIView):
    serializer_class = Outlook_CommentSerializer
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        queryset = OutlookCommentModel.objects.filter(is_reply=IsReplyEnum.NO.value).order_by('-created_at')
        news = request.query_params.get('news')
        if news:
            queryset = queryset.filter(news=news)
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = Outlook_CommentSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    
class Outlook_LikeCommentView(APIView):
    def post(self, request, *args, **kwargs):
        comment_id = kwargs.get('comment_id')
        try:
            comment = OutlookCommentModel.objects.get(_id=comment_id)
            if comment.likes is None:
                comment.likes = 0
            comment.likes += 1
            comment.save()
            return Response({"status": "comment liked"}, status=status.HTTP_200_OK)
        except OutlookCommentModel.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)


class Outlook_DislikeCommentView(APIView):
    def post(self, request, *args, **kwargs):
        comment_id = kwargs.get('comment_id')
        try:
            comment = OutlookCommentModel.objects.get(_id=comment_id)
            if comment.dislikes is None:
                comment.dislikes = 0
            comment.dislikes += 1
            comment.save()
            return Response({"status": "comment disliked"}, status=status.HTTP_200_OK)
        except OutlookCommentModel.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)