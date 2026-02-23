import uuid
from django.db import models


class ArticleCategory(models.Model):
    _id = models.CharField(db_column='_id', primary_key=True, max_length=45, default=uuid.uuid1, unique=True, editable=False)
    name = models.CharField(db_column='name', max_length=100, unique=True)
    profile_pic= models.TextField(blank=True, null=True)
    
    
    class Meta:
        db_table = "article_category"
        
    
 