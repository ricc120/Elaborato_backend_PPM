import requests
from datetime import datetime
from django.core.management import BaseCommand
from forecasts.models import SimulatedForecast

class Command(BaseCommand):
    help = 'Populates the database with real and updated weather data from Open-Meteo'

    def handle(self, *args, **options):
        cities = [
            {'name': 'Rome', 'lat': 41.8919, 'lon': 12.5113},
            {'name': 'Milan', 'lat': 45.4643, 'lon': 9.1895},
            {'name': 'Naples', 'lat': 40.8522, 'lon': 14.2681},
            {'name': 'Florence', 'lat': 43.7696, 'lon': 11.2558},
        ]

        self.stdout.write(self.style.SUCCESS("Starts scraping weather data from Open-Meteo..."))

        for city in cities:
            url = 'https://api.open-meteo.com/v1/forecast'
            params = {
                'latitude': city['lat'],
                'longitude': city['lon'],
                'daily': 'temperature_2m_max,relative_humidity_2m_max,weather_code',
                'time_zone': 'Europe/Rome'
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                daily_data = data.get('daily', {})
                dates = daily_data.get('time', [])
                max_temps = daily_data.get('temperature_2m_max', [])
                humidities = daily_data.get('relative_humidity_2m_max', [])
                weather_codes = daily_data.get('weather_code', [])

                for i in range(len(dates)):
                    # Converts date string (YYYY-MM-DD) in Python object date
                    date_obj = datetime.strptime(dates[i], '%Y-%m-%d').date()

                    # Converts Open-Meteo code WMO in a textual description
                    condition = self.map_wmo_code_to_string(weather_codes[i])

                    # Avoid duplicates if you run the command multiple times in the same day
                    forecast, created = SimulatedForecast.objects.get_or_create(
                        location=city['name'],
                        date=date_obj,
                        defaults={
                            'temperature': max_temps[i],
                            'humidity': int(humidities[i]) if humidities[i] is not None else 50,
                            'condition': condition,
                        }
                    )

                self.stdout.write(self.style.SUCCESS(f"Dates updated with success for: {city['name']}"))

            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Error retrieving data for: {city['name']} "))

            self.stdout.write(self.style.SUCCESS("Database populated correctly!"))

    def map_wmo_code_to_string(self, code):
        """
        Maps standard WMO weather codes in readable strings
        """
        if code == 0:
            return "Sunny"
        elif code in [1, 2, 3]:
            return "Cloudy"
        elif code in [45, 48]:
            return "Foggy"
        elif code in [51, 53, 55, 61, 63, 65]:
            return "Rainy"
        elif code in [71, 73, 75, 77, 85, 86]:
            return "Snowy"
        elif code in [95, 96, 99]:
            return "Stormy"
        else:
            return "Variable"

