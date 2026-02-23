from django.db import models
import uuid

class FixedHoliday(models.Model):
    _id = models.CharField(db_column='_id', primary_key=True, max_length=45, default=uuid.uuid1, unique=True, editable=False)
    date = models.DateField(unique=True)  # Unique date for the holiday
    description = models.CharField(max_length=255)  # Description of the holiday

    def __str__(self):
        return f"{self.date}: {self.description}"
    
    class Meta:
        managed = True
        db_table = 'fixed_holidays'