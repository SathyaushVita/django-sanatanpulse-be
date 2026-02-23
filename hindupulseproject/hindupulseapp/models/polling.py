from django.db import models
from .register import Register
from .news_subcategory import NewsSubCategory
import uuid

class Poll(models.Model):
    _id = models.CharField(db_column='_id', primary_key=True, max_length=45, default=uuid.uuid1, unique=True, editable=False)
    other_category = models.ForeignKey(NewsSubCategory, db_column='other_category',max_length=45, on_delete=models.CASCADE, related_name='poll_status')
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'poll'

class PollResponse(models.Model):
    _id = models.CharField(db_column='_id', primary_key=True, max_length=45, default=uuid.uuid1, unique=True, editable=False)
    poll = models.ForeignKey(Poll, db_column='Poll', on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(Register,db_column='user', on_delete=models.CASCADE,related_name='polling_user')
    response = models.CharField(max_length=3, choices=[('YES', 'Yes'), ('NO', 'No')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('poll', 'user')  # Ensure one response per user per poll
        db_table = 'poll_responce'
