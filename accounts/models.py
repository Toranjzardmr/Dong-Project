from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.

class CustomUser(AbstractUser):

    email = models.EmailField(max_length=150,unique=True)
    profile_photo = models.ImageField(
        upload_to='profiles/',
        null= True,
        blank= True,
    )

    friends = models.ManyToManyField(
        'self',
        symmetrical=True,
        blank=True,
        related_name='friends_with',
    )

    def __str__(self):
        return self.username