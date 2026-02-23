from django.db import models
# from .articles import ArticleModel
import uuid
from ..enums import MemberStatus
from ..enums import EntityStatus

class ArticleProfile(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=45, default=uuid.uuid1, unique=True, editable=False)
    name = models.CharField(max_length=200,blank=True, null=True)
    profile_pic= models.TextField(blank=True, null=True)
    desc = models.CharField(db_column='desc', blank=True, null=True, max_length=5000)
    email=models.EmailField()
    article=models.ForeignKey('ArticleModel', on_delete=models.SET_NULL, related_name='article_model', null=True,db_column='article')
    is_member=models.CharField(max_length=50,choices=[(e.name,e.value) for e in MemberStatus],default=MemberStatus.false.value)
    status = models.CharField(max_length=50, choices=[(e.name, e.value) for e in EntityStatus], default=EntityStatus.PENDING.value)
    
    class Meta:
        db_table = "article_profile"
  