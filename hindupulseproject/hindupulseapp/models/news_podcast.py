from django.db import models
import uuid
from .register import Register
from ..enums import EntityStatus

class NewsPodcast(models.Model):
    _id = models.CharField(db_column='_id', primary_key=True, max_length=45 ,default=uuid.uuid1, unique=True ,editable=False)
    name = models.CharField(db_column='name', max_length=5000) 
    desc = models.CharField(db_column='desc', max_length=25000, blank=True, null=True) 
    image_location = models.TextField(db_column='image_location',blank=True, null=True) 
    news_link = models.URLField(db_column='news_link',max_length=5000,blank=True,null=True,help_text="Original news article link")
    user = models.ForeignKey(Register, on_delete=models.SET_NULL, related_name='news_podcast', null=True,db_column="user")
    status = models.CharField(max_length=50, choices=[(e.name, e.value) for e in EntityStatus], default=EntityStatus.PENDING.value)
    video_location= models.TextField(db_column='video_location',blank=True, null=True) 

    def __str__(self):
        return self.name

    class Meta:
        managed=False
        db_table = 'news_podcast'  










