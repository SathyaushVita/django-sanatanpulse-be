# from rest_framework import serializers
# from ..models import ArticleProfile,ArticleModel
# from ..utils import image_path_to_binary
# from .article_serializers import ArticleSerializer1,ArticleSerializer
# from django.core.validators import RegexValidator
# from django import forms




# class ArticleProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ArticleProfile
#         fields = ["id","name","profile_pic","desc","email","article"]

# class ArticleProfileSerializer1(serializers.ModelSerializer):

#     profile_pic = serializers.SerializerMethodField()
   
#     article_user = ArticleSerializer1(many=True, read_only=True)

   

#     def get_profile_pic(self, instance):
#         filename = instance.profile_pic
#         if filename:
#             # Assuming image_path_to_binary is a utility function you have defined
#             format = image_path_to_binary(filename)
#             return format
#         return []

#     class Meta:
#         model = ArticleProfile
#         fields = '__all__'

from rest_framework import serializers
from ..models import ArticleProfile,ArticleModel
from ..utils import image_path_to_binary
from .article_serializers import ArticleSerializer1,ArticleSerializer
from django.core.validators import RegexValidator
from django import forms


from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from ..models import ArticleProfile, ArticleModel
from ..serializers import ArticleSerializer1  # Ensure this serializer is defined



class ArticleProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleProfile
        fields = ["id","name","profile_pic","desc","email","article","status"]

class PaginatedArticleSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = serializers.ListField(child=ArticleSerializer1())

class ArticleProfileSerializer1(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()
    article_user = serializers.SerializerMethodField()

    def get_profile_pic(self, instance):
        filename = instance.profile_pic
        if filename:
            format = image_path_to_binary(filename)
            return format
        return []

    def get_article_user(self, instance):
        request = self.context.get('request')
        articles = instance.article_user.all()  # Retrieve related articles
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the page size according to your needs
        paginated_articles = paginator.paginate_queryset(articles, request)
        serialized_articles = ArticleSerializer1(paginated_articles, many=True, context={'request': request}).data

        return {
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'results': serialized_articles,
        }

    class Meta:
        model = ArticleProfile
        fields = '__all__'
