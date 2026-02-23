# import uuid
# from .news_subcategory import NewsSubCategory
# from django.db import models
# from ..enums import EntityStatus



# class Leader(models.Model):

#     _id = models.CharField(db_column='_id', primary_key=True, max_length=45, default=uuid.uuid1, unique=True, editable=False)
#     name = models.CharField(db_column='name', max_length=100)
#     desc = models.TextField(db_column='desc', blank=True, null=True)
#     profile_pic= models.TextField(blank=True, null=True)
#     organization_link=models.JSONField(default=list, blank=True, null=True)
#     status = models.CharField(max_length=50, choices=[(e.name, e.value) for e in EntityStatus], default=EntityStatus.PENDING.value)
#     location=models.CharField(db_column='location',max_length=45,null=True,)
#     created_at = models.DateTimeField(auto_now_add=True)
    

#     # other_category = models.ForeignKey(NewsSubCategory, db_column='category_id1',max_length=45, on_delete=models.CASCADE, related_name='category_id1')
    

#     class Meta:
#         db_table = "leader"
        