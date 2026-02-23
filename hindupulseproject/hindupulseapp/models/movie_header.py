from django.db import models
import uuid

class MovieHeader(models.Model):
    _id = models.CharField(db_column='_id', primary_key=True, max_length=45 ,default=uuid.uuid1, unique=True ,editable=False)
    name = models.CharField(max_length=255)
    desc = models.TextField()

    class Meta:
        db_table = 'movie_header'

    def __str__(self):
        return self.name
