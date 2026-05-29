from django.db import models
from django.conf import settings
from setuptools.command.bdist_egg import make_zipfile

from users.models import CustomUser


# Create your models here.
class SimulatedForecast(models.Model):
    """
    Contains simulated weather data
    """
    location = models.CharField(max_length=100, db_index=True)
    date = models.DateField()
    temperature = models.FloatField()
    humidity = models.IntegerField(help_text="Percentage humidity")
    condition = models.CharField(max_length=50, help_text="Ex. Sunny, Rainy, Cloudy")

    class Meta:
        unique_together = ('location', 'date')

    def __str__(self):
        return f"{self.location} - {self.date}: {self.temperature}"

class SavedQuery(models.Model):
    """
    Manages the history of saved queries, exclusively for Premium User.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_queries'
    )
    location = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} searched {self.location} at {self.timestamp}"

class DailyRequestTracker(models.Model):
    """
    Traces the number of daily requests to apply limits for Basic or Anonymous users
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='daily_requests'
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the request"
    )

    date = models.DateField(auto_now=True)
    request_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Request of {self.user.username} at {self.date}: {self.request_count}"