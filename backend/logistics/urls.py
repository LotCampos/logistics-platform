from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router=DefaultRouter()
for prefix, cls in [('vehicles',VehicleViewSet),('services',ServiceScheduleViewSet),('trips',TripViewSet),('routes',RouteViewSet),('route-stops',RouteStopViewSet),('travel-budgets',TravelBudgetViewSet),('travel-expenses',TravelExpenseViewSet),('maintenance',MaintenanceOrderViewSet),('fuel',FuelTransactionViewSet)]: router.register(prefix,cls)
urlpatterns=[path('',include(router.urls))]
