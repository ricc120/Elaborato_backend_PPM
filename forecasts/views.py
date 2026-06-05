from django.shortcuts import render
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework import status,permissions, viewsets
from django.utils.timezone import now
from .models import SimulatedForecast, DailyRequestTracker, SavedQuery, FavouriteCity
from .serializers import SimulatedForecastSerializer, SavedQuerySerializer, FavouriteCitySerializer
from django.db.models import Count, Max

# Create your views here.

class WeatherForecastView(APIView):

    # Allows access to everybody, manages roles within the GET method
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        location = request.query_params.get('location')
        date_str = request.query_params.get('date')
        time_str = request.query_params.get('time')

        user = request.user if request.user.is_authenticated else None
        # Checks roles (AuthZ)
        is_premium = user and getattr(user, 'role', '') == 'premium'

        # Searches Premium user favourite city if he's not insert 'location' in URL
        if not location and is_premium:
            primary_fav = FavouriteCity.objects.filter(user=user, is_primary=True).first()
            if primary_fav:
                location = primary_fav.name

        # Input validation, location is mandatory
        if not location:
            return Response(
                {'error': 'Parameter "location" is required or set a primary favourite city.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Input validation, date is optional
        target_date = None
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid data format. Use: YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        target_time = None
        if time_str:
            try:
                target_time = datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                return Response(
                    {'error': 'Invalid data format. Use: HH:MM'},
                    status=status.HTTP_400_BAD_REQUEST
                )

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

        if target_date:
            forecasts = forecasts.filter(date=target_date)

        if target_time:
            forecasts = forecasts.filter(time=target_time)

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

class IsEditorOrReadOnly(permissions.BasePermission):
    """
    Allows GET, HEAD or OPTIONS requests to all users.
    Allows POST, PUT or DELETE requests to editor users only.
    """

    def has_permission(self, request, view):

        # SAFE_METHODS are read-only methods
        if request.method in permissions.SAFE_METHODS:
            return True

        # Verifies that the user is logged in and is an editor
        return bool(
            request.user and request.user.is_authenticated and
            getattr(request.user, 'role','')== 'editor'
        )

class ForecastManagementViewSet(viewsets.ModelViewSet):
    queryset = SimulatedForecast.objects.all().order_by('-date', 'time')
    serializer_class = SimulatedForecastSerializer
    # Applies custom permission
    permission_classes = [IsEditorOrReadOnly]

class FavouriteCityViewSet(viewsets.ModelViewSet):
    serializer_class = FavouriteCitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', '') != 'premium':
            raise PermissionDenied("Only premium users can save favourite cities")

        return FavouriteCity.objects.filter(user=user).order_by('is_primary', 'name')

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, 'role', '') != 'premium':
            raise PermissionDenied("Only premium users can save favourite cities")

        # Sets the first city saved as primary by default
        is_first = not FavouriteCity.objects.filter(user=user).exists()
        is_primary = self.request.data.get('is_primary', is_first)

        serializer.save(user=user, is_primary=is_primary)

class HistoryStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if getattr(user, 'role', '') != 'premium':
            raise PermissionDenied("Only premium users can access statistics")

        queries = SavedQuery.objects.filter(user=user)
        total_queries = queries.count()

        if total_queries == 0:
            return Response(
                {'message': 'No queries found to calculate statistics' },
                status=status.HTTP_200_OK
            )

        # Uses ORM to found the most searched cities byt grouping (GROUP BY) and counting (COUNT)
        top_city = queries.values('location').annotate(total=Count('location')).order_by('-total').first()

        # Finds the date of the last research
        last_search = queries.aggregate(latest=Max('timestamp'))

        return Response(
            {'total_searches_made': total_queries,
             'most_searched_city': top_city['location'] if top_city else None,
             'times_searched': top_city['total'] if top_city else 0,
             'last_active': last_search['latest'] if last_search else None,
             },
            status=status.HTTP_200_OK
        )