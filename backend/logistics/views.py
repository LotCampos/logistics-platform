from rest_framework import viewsets
from django.db.models import Sum, Count
from .models import *
from .serializers import *

class VehicleViewSet(viewsets.ModelViewSet):
    queryset=Vehicle.objects.all(); serializer_class=VehicleSerializer; filterset_fields=['status','vehicle_type','fuel_type']
class ServiceScheduleViewSet(viewsets.ModelViewSet):
    queryset=ServiceSchedule.objects.all().order_by('scheduled_start'); serializer_class=ServiceScheduleSerializer; filterset_fields=['status','client_id','installation_id','vehicle','priority']
class TripViewSet(viewsets.ModelViewSet):
    queryset=Trip.objects.all().order_by('-departure_at'); serializer_class=TripSerializer; filterset_fields=['status','vehicle']
class RouteViewSet(viewsets.ModelViewSet):
    queryset=Route.objects.all(); serializer_class=RouteSerializer
class RouteStopViewSet(viewsets.ModelViewSet):
    queryset=RouteStop.objects.all(); serializer_class=RouteStopSerializer
class TravelBudgetViewSet(viewsets.ModelViewSet):
    queryset=TravelBudget.objects.all(); serializer_class=TravelBudgetSerializer; filterset_fields=['status','currency']
class TravelExpenseViewSet(viewsets.ModelViewSet):
    queryset=TravelExpense.objects.all(); serializer_class=TravelExpenseSerializer; filterset_fields=['category','budget']
class MaintenanceOrderViewSet(viewsets.ModelViewSet):
    queryset=MaintenanceOrder.objects.all().order_by('-scheduled_at'); serializer_class=MaintenanceOrderSerializer; filterset_fields=['status','vehicle']
class FuelTransactionViewSet(viewsets.ModelViewSet):
    queryset=FuelTransaction.objects.all().order_by('-occurred_at'); serializer_class=FuelTransactionSerializer; filterset_fields=['vehicle']

def dashboard_data():
    return {'services':ServiceSchedule.objects.values('status').annotate(total=Count('id')),'fleet':Vehicle.objects.values('status').annotate(total=Count('id')),'travel_expenses':TravelExpense.objects.aggregate(estimated=Sum('estimated'),actual=Sum('actual'))}
