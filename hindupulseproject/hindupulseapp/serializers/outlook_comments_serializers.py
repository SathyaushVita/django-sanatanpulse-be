
from rest_framework import serializers
from ..models import OutlookCommentModel, Register
from ..utils import image_path_to_binary
from ..enums.is_reply_enum import IsReplyEnum

class Outlook_ReplySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)

    def get_user(self, instance):
        try:
            user = instance.user
            if user:
                profile_pic_path = user.profile_pic
                if profile_pic_path:
                    base64_profile_pic = image_path_to_binary(profile_pic_path)
                    return {
                        "surname": user.surname,
                        "full_name": user.full_name,
                        "id": user.id,
                        "profile_pic": base64_profile_pic if base64_profile_pic else None,
                    }
                else:
                    return {
                        "surname": user.surname,
                        "full_name": user.full_name,
                        "id": user.id,
                        "profile_pic": None,
                    }
            return None
        except Register.DoesNotExist:
            return None

    class Meta:
        model = OutlookCommentModel
        fields = ['_id', 'body', 'user', 'created_at','likes', 'dislikes']


class Outlook_CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    replies = Outlook_ReplySerializer(many=True, read_only=True)

    def get_user(self, instance):
        try:
            user = instance.user
            if user:
                profile_pic_path = user.profile_pic
                if profile_pic_path:
                    base64_profile_pic = image_path_to_binary(profile_pic_path)
                    return {
                        "surname": user.surname,
                        "full_name": user.full_name,
                        "id": user.id,
                        "profile_pic": base64_profile_pic if base64_profile_pic else None,
                    }
                else:
                    return {
                        "surname": user.surname,
                        "full_name": user.full_name,
                        "id": user.id,
                        "profile_pic": None,
                    }
            return None
        except Register.DoesNotExist:
            return None

    class Meta:
        model = OutlookCommentModel
        fields = ['_id', 'body', 'user', 'news', 'replies', 'created_at','is_reply', 'likes', 'dislikes']


class Outlook_CommentSerializer1(serializers.ModelSerializer):
    class Meta:
        model = OutlookCommentModel
        fields = ['_id', 'body', 'user', 'news', 'parent']