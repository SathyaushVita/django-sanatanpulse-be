
from django.db import models
import uuid
from .register import Register
from ..enums.is_reply_enum import IsReplyEnum

class NewsCommentModel(models.Model):
    _id = models.CharField(db_column='_id', primary_key=True, max_length=45, default=uuid.uuid1, unique=True, editable=False)
    user = models.ForeignKey(Register, on_delete=models.SET_NULL, related_name='news_comment_user', null=True, db_column='user')
    news = models.ForeignKey('NewsCategory', db_column='news', on_delete=models.CASCADE, max_length=1000, blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    body = models.CharField(db_column='body', max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_reply = models.CharField(max_length=50, choices=[(e.name, e.value) for e in IsReplyEnum], default=IsReplyEnum.NO.value)
    likes = models.IntegerField(default=0)  # Ensure default value is 0
    dislikes = models.IntegerField(default=0)  # Ensure default value is 0

    class Meta:
        managed = True
        db_table = 'news_comment'
