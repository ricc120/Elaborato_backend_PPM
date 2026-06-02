from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework import status,permissions, viewsets
from django.utils.timezone import now
from .models import SimulatedForecast, DailyRequestTracker, SavedQuery
from .serializers import SimulatedForecastSerializer, SavedQuerySerializer

# Create your views here.

class WeatherForecastView(APIView):
    # Allows access to everybody, manages roles within the GET method
    permissions_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        location = request.query_params.get('location')

        # Input validation
        if not location:
            return Response(
                {'error': 'Parameter "location" is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user if request.user.is_authenticated else None

        # Checks roles (AuthZ)
        is_premium = user and getattr(user, 'role', '') == 'premium'

        # Manages rate-limit logics for no premium users
        if not is_premium:
            ip_address = request.META.get('REMOTE_ADDR')
            today = now().date()

            # get_or_create avoids double queries
            tracker, created = DailyRequestTracker.objects.get_or_create(
                user=user if user else None,
                ip_address=ip_address if not user else None,
                date=today,
            )

            # Sets five request per day for basic/anonymous users
            if tracker.request_count >= 5:
                return Response(
                    {'error': 'Request limit reached, upgrade to premium'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            tracker.request_count += 1
            tracker.save()

        # Retrieves dates through ORM
        forecasts = SimulatedForecast.objects.filter(location__iexact=location)

        if not forecasts.exists():
            return Response(
                {'error': 'No forecast found for this location'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Saves automatically to history from premium users
        if is_premium:
            SavedQuery.objects.create(user=user, location=location)

        serializer = SimulatedForecastSerializer(forecasts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SavedQueryViewSet(viewsets.ModelViewSet):
    serializer_class = SavedQuerySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', '') != 'premium':
            raise PermissionDenied("Only premium users can access to the history")

        return SavedQuery.objects.filter(user=user).order_by('-timestamp')

    def perform_create(self, serializer):
        # Forces assignment to the account of a user who created a query manually
        user = self.request.user
        if getattr(user, 'role', '') != 'premium':
            raise PermissionDenied("Only premium users can save researches")
        serializer.save(user=user)