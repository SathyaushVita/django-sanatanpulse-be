import uuid
from .organizations_category import OrganizationCategory
from django.db import models
from ..enums import EntityStatus



class Organizations(models.Model):

    _id = models.CharField(db_column='_id', primary_key=True, max_length=45, default=uuid.uuid1, unique=True, editable=False)
    name = models.CharField(db_column='name', max_length=100)
    desc = models.TextField(db_column='desc', blank=True, null=True)
    profile_pic= models.TextField(blank=True, null=True)
    organization_link=models.JSONField(default=list, blank=True, null=True)
    status = models.CharField(max_length=50, choices=[(e.name, e.value) for e in EntityStatus], default=EntityStatus.PENDING.value)
    organization_category = models.ForeignKey(OrganizationCategory, db_column='organization_category',max_length=45, on_delete=models.CASCADE, related_name='organization_category')
    created_at = models.DateTimeField(auto_now_add=True)
    location=models.CharField(db_column='location',max_length=45,null=True,)
    priority_order = models.IntegerField(default=0)
    

    class Meta:
        db_table = "organizations"
        
