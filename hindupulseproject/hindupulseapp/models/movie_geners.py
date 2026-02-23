from django.db import models
import uuid

class MovieGeners(models.Model):
    _id = models.CharField(db_column='_id', primary_key=True, max_length=45 ,default=uuid.uuid1, unique=True ,editable=False)
    header = models.ForeignKey('MovieHeader',on_delete=models.CASCADE,related_name='geners')
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'movie_all_geners'

    def __str__(self):
        return self.name
