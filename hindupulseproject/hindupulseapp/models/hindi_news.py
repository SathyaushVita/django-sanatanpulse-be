

import uuid
from .category import Category
from .news_subcategory import NewsSubCategory
from django.db import models
from ..enums import EntityStatus,LanguageEnum
from ..enums import EntityStatus,LanguageEnum,IsPublish
# from .languages import Language
from .register import Register





class HindiNews(models.Model):
    _id = models.CharField(db_column='_id', primary_key=True, max_length=45, default=uuid.uuid1, unique=True, editable=False)
    headline = models.CharField(db_column='headline',max_length=500)
    desc = models.TextField(db_column='desc', blank=True, null=True)
    short_description = models.CharField(db_column='short_description', blank=True, null=True, max_length=1500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # This will update on every modification
    location=models.CharField(db_column='location',max_length=45,null=True,)
    status = models.CharField(max_length=50, choices=[(e.name, e.value) for e in EntityStatus], default=EntityStatus.PENDING.value)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE,null=True, max_length=45, related_name='hindi_category_id')
    news_sub_category_id = models.ForeignKey(NewsSubCategory,null=True, on_delete=models.CASCADE,related_name="hindi_news_sub_category_id")
    image_location = models.JSONField(default=list, blank=True, null=True)
    audio_location = models.TextField(blank=True, null=True)  # New audio field
    # language_id = models.ForeignKey(Language, on_delete=models.CASCADE,null=True,related_name='languageList')
    # publish_at = models.DateTimeField(null=True, blank=True)  # New field to schedule when the news article is published
    language = models.CharField(db_column='language',max_length=50, choices=[(e.name, e.value) for e in LanguageEnum], default=LanguageEnum.HINDI.value)
    user = models.ForeignKey(Register, on_delete=models.SET_NULL, related_name='hindi_add_news', null=True)
    url = models.URLField(max_length=5000, null=True, blank=True)
    is_published = models.CharField(db_column='is_published',max_length=50,choices=[(e.name, e.value) for e in IsPublish],default=IsPublish.NOT_PUBLISHED.value)
    publish_at = models.DateTimeField(null=True, blank=True)  # Field to schedule when the news is published



            
    class Meta:
        managed = False
        db_table = "hindi_news"
 





