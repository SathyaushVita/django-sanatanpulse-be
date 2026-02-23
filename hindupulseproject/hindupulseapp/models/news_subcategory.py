import uuid
from .category import Category
from django.db import models



class NewsSubCategory(models.Model):

    _id = models.CharField(db_column='_id', primary_key=True, max_length=45, default=uuid.uuid1, unique=True, editable=False)
    name = models.CharField(db_column='name', max_length=100)
    other_category = models.ForeignKey(Category, db_column='category_id1',max_length=45, on_delete=models.CASCADE, related_name='category_id1')
    

    class Meta:
        db_table = "sub_category"
        
