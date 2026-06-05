from django.contrib import admin
from forecasts.models import SimulatedForecast, SavedQuery, DailyRequestTracker, FavouriteCity

# Register your models here.

admin.site.register(SimulatedForecast)
admin.site.register(SavedQuery)
admin.site.register(DailyRequestTracker)
admin.site.register(FavouriteCity)
