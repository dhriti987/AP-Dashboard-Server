from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    contact_no = models.CharField(max_length=20)
    employee_id = models.CharField(max_length=20)
