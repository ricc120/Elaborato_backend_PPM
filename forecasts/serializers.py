from rest_framework import serializers
from .models import SimulatedForecast, SavedQuery, FavouriteCity

class SimulatedForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulatedForecast
        fields = ['id', 'location', 'date', 'time', 'temperature', 'humidity', 'condition']

class SavedQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedQuery
        fields = ['id', 'location', 'timestamp']
        read_only_fields = ['id', 'timestamp']

class FavouriteCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouriteCity
        fields = ['id', 'name', 'is_primary']


