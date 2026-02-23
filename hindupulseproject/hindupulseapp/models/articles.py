import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.timesince import timesince
from .register import Register
from .article_profile import ArticleProfile
from ..enums import EntityStatus
from django.core.validators import RegexValidator
from .article_category import ArticleCategory
from ..enums import EntityStatus,LanguageEnum,IsPublish
from datetime import datetime
def current_year():
    return datetime.now().year



class ArticleModel(models.Model):
    _id = models.CharField(db_column='_id', primary_key=True, max_length=45, default=uuid.uuid1, unique=True, editable=False)
    headline = models.TextField(db_column='headline', blank=True, null=True)
    desc = models.TextField(db_column='desc', blank=True, null=True)
    short_description = models.TextField(db_column='short_description', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # This will update on every modification
    location=models.CharField(db_column='location',max_length=45,null=True,)
    status = models.CharField(max_length=50, choices=[(e.name, e.value) for e in EntityStatus], default=EntityStatus.PENDING.value)
    category_id = models.ForeignKey(ArticleCategory, on_delete=models.CASCADE,null=True, max_length=45, related_name='category_id',db_column='category_id')
    # news_sub_category_id = models.ForeignKey(NewsSubCategory,null=True, on_delete=models.CASCADE,related_name="news_sub_category_id")
    image_location = models.JSONField(default=list, blank=True, null=True)
    audio_location = models.TextField(blank=True, null=True)  # New audio field
    # language_id = models.ForeignKey(Language, on_delete=models.CASCADE,null=True,related_name='languageList')
    # publish_at = models.DateTimeField(null=True, blank=True)  # New field to schedule when the news article is published
    language = models.CharField(db_column='language',max_length=50, choices=[(e.name, e.value) for e in LanguageEnum], default=LanguageEnum.ENGLISH.value)
    user = models.ForeignKey(Register, on_delete=models.SET_NULL, related_name='user', null=True,db_column='user')
    article_user = models.ForeignKey(ArticleProfile, on_delete=models.SET_NULL, related_name='article_user', null=True,db_column='article_user')
    # url = models.URLField(max_length=5000, null=True, blank=True)
    is_published = models.CharField(db_column='is_published',max_length=50,choices=[(e.name, e.value) for e in IsPublish],default=IsPublish.NOT_PUBLISHED.value)
    publish_at = models.DateTimeField(null=True, blank=True)  # Field to schedule when the news is published  
    date = models.CharField(
        max_length=4,
        null=True,
        validators=[RegexValidator(regex=r'^\d{4}$', message='Enter a valid year.')],
        help_text='Enter the year in YYYY format.'
    )
    
    
    def __str__(self):
        return self.name 
  


    class Meta:
        db_table = "articles"


###############################################this is pdf_location code ##################################
# import uuid
# from django.db import models
# from django.contrib.auth.models import User
# from django.utils.timesince import timesince
# from .register import Register
# from .article_profile import ArticleProfile
# from ..enums import EntityStatus
# from django.core.validators import RegexValidator
# from .article_category import ArticleCategory
# from datetime import datetime
# def current_year():
#     return datetime.now().year

# class ArticleModel(models.Model):
#     _id = models.CharField(db_column='_id', primary_key=True, max_length=45, default=uuid.uuid1, unique=True, editable=False)
#     name = models.CharField(db_column='name', max_length=100)
#     article_user = models.ForeignKey(ArticleProfile, on_delete=models.SET_NULL, related_name='article_user', null=True,db_column='article_user')
#     category_id = models.ForeignKey(ArticleCategory, on_delete=models.CASCADE, max_length=45, related_name='category_id',db_column='category_id')
#     user = models.ForeignKey(Register, on_delete=models.SET_NULL, related_name='user', null=True,db_column='user')
#     pdf_location = models.TextField(blank=True, null=True)
#     image_location = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=50, choices=[(e.name, e.value) for e in EntityStatus], default=EntityStatus.PENDING.value)
#     date = models.CharField(
#         max_length=4,
#         null=True,
#         validators=[RegexValidator(regex=r'^\d{4}$', message='Enter a valid year.')],
#         help_text='Enter the year in YYYY format.'
#     )

    
    
    
    
#     def __str__(self):
#         return self.name 
  


#     class Meta:
#         db_table = "articles"