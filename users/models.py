from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class CustomUser(AbstractUser):

    ROLE_CHOICES = [
        ('regular', 'Regular User'),
        ('premium', 'Premium User'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='regular',
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()}"
