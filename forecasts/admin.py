from django.contrib import admin
from forecasts.models import SimulatedForecast, SavedQuery, DailyRequestTracker

# Register your models here.

admin.site.register(SimulatedForecast)
admin.site.register(SavedQuery)
admin.site.register(DailyRequestTracker)
