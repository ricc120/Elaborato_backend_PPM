from rest_framework import serializers
from .models import SimulatedForecast, SavedQuery

class SimulatedForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulatedForecast
        fields = ['location', 'date', 'time', 'temperature', 'humidity', 'condition']

class SavedQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedQuery
        fields = ['id', 'location', 'timestamp']
        read_only_fields = ['id', 'timestamp']


