

from django.db import models
from ..enums.user_status_enum import UserStatus
import uuid
# import datetime
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
# from ..utils import send_email,generate_otp,validate_email,send_sms
from django.dispatch import receiver
from django.db.models.signals import post_save
from ..enums.member_type_enum import MemberType
from ..enums.member_status_enum import MemberStatus 
from ..enums.gender_enum import Gender
# from ..enums.member_visibility_enum import MemberVisibility


class Register(AbstractUser):
    id = models.CharField(db_column='id', primary_key=True, max_length=45, default=uuid.uuid1, unique=True, editable=False) 
    full_name = models.CharField(max_length=200,blank=True, null=True)
    surname = models.CharField(max_length=200,db_column='surname')
    full_name = models.CharField(max_length=200,db_column='full_name')
    father_name=models.CharField(max_length=200)
    contact_number=models.CharField(max_length=10,unique=True)
    profile_pic= models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=50,choices=[(e.name,e.value) for e in Gender],default=Gender.MALE.value)
    dob = models.DateField()
    gotram = models.CharField(max_length=200, blank=True) 
    verification_otp = models.CharField(max_length=6, null=True, blank=True)
    verification_otp_created_time = models.DateTimeField(null=True)
    verification_otp_resend_count = models.IntegerField(default=0)
    status = models.CharField(max_length=50, choices=[(e.name, e.value) for e in UserStatus], default=UserStatus.CREATED.value)
    forgot_password_otp = models.CharField(max_length=6, null=True, blank =True)
    forgot_password_otp_created_time = models.DateTimeField(null=True)
    forgot_password_otp_resend_count = models.IntegerField(default=0)
    is_member=models.CharField(max_length=50,choices=[(e.name,e.value) for e in MemberStatus],default=MemberStatus.false.value)
    type=models.CharField(db_column="type",max_length=50,choices=[(e.name,e.value) for e in MemberType],default=MemberType.MEMBER.value)
    pujari_certificate = models.TextField(db_column='pujari_certificate',null=True,blank=True)
    working_temple = models.CharField(db_column='working_temple',max_length=150, null=True, blank=True)
    account_type = models.CharField(max_length=10)
    stakeholder_type=models.CharField(max_length=10)
    family_images = models.JSONField(default=list, blank=True)
    # member_visibility = models.CharField(
    #     max_length=50,
    #     choices=[(e.name, e.value) for e in MemberVisibility],
    #     default=MemberVisibility.PUBLIC.value
    # )




        
    class Meta:
        db_table = "user"

    
    def __str__(self):
        return self.username

    def generate_verification_otp(self):
        import random
        self.verification_otp = str(random.randint(1000, 9999))
        self.verification_otp_created_time = timezone.now()
        self.verification_otp_resend_count = 0
        self.save()

    