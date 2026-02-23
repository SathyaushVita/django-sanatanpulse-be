# from django.db import models
# import uuid
# from ..enums import LanguageEnum


# class Language(models.Model):
#     _id = models.CharField(db_column='_id', primary_key=True, max_length=45, default=uuid.uuid1, unique=True, editable=False)
#     name = models.CharField(max_length=100, choices=[(e.name, e.value) for e in LanguageEnum])
    
    
#     class Meta:
#         db_table = "language"





from django.db import models
import uuid
from ..enums import LanguageEnum


class Language(models.Model):
    _id = models.CharField(db_column='_id', primary_key=True, max_length=45, default=uuid.uuid1, unique=True, editable=False)
    name = models.CharField(max_length=100,null=True,blank=True)
    
    
    class Meta:
        db_table = "language"
