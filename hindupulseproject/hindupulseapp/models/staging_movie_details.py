from django.db import models
import uuid
from ..enums import MovieStatus
from .register import Register
from .movie_geners import MovieGeners
from .movie_header import MovieHeader
from .movie_platforms import MoviePlatforms
from .languages import Language
 
class StagingMovieDetails(models.Model):
    _id = models.CharField(db_column='_id', primary_key=True, max_length=45 ,default=uuid.uuid1, unique=True ,editable=False)
    title = models.CharField(max_length=100,null=True, blank=True)
    header_id = models.ForeignKey(MovieHeader,on_delete=models.CASCADE,related_name="staging_movie_details",db_column="header_id",blank=True, null=True)
    poster = models.JSONField(db_column='poster', blank=True, null=True)
    release_date = models.CharField(max_length=100,null=True, blank=True)
    cast = models.TextField(null=True, blank=True)
    trailer = models.JSONField(db_column='trailer', blank=True, null=True,default=list)
    actions = models.TextField(null=True, blank=True)
    platform_id = models.ForeignKey(MoviePlatforms,on_delete=models.CASCADE,related_name='staging_movie_details',db_column='platform_id',blank=True, null=True )
    status = models.CharField(max_length=50, choices=[(e.name, e.value) for e in MovieStatus], default=MovieStatus.STAGING.value)
    geners_id = models.ForeignKey(MovieGeners,on_delete=models.CASCADE,related_name="staging_movie_details",db_column="geners_id",blank=True, null=True)
    user_id = models.ForeignKey(Register, on_delete=models.SET_NULL, related_name='staging_movie_details', null=True,blank=True, db_column='user_id')
    language = models.ForeignKey(Language,on_delete=models.CASCADE,related_name="staging_movie_details",db_column="language",blank=True, null=True)
    publish_at = models.DateTimeField(null=True, blank=True)  # Field to schedule when the details is published
    trailer_link=models.URLField(null=True,blank=True)

    class Meta:
            managed = True
            db_table = "staging_movie_details"

 
