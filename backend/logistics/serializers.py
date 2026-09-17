from rest_framework import serializers
from .models import *

class VehicleSerializer(serializers.ModelSerializer):
    class Meta: model=Vehicle; fields='__all__'
class ServiceScheduleSerializer(serializers.ModelSerializer):
    class Meta: model=ServiceSchedule; fields='__all__'
class TripSerializer(serializers.ModelSerializer):
    class Meta: model=Trip; fields='__all__'
class RouteSerializer(serializers.ModelSerializer):
    class Meta: model=Route; fields='__all__'
class RouteStopSerializer(serializers.ModelSerializer):
    class Meta: model=RouteStop; fields='__all__'
class TravelBudgetSerializer(serializers.ModelSerializer):
    class Meta: model=TravelBudget; fields='__all__'
class TravelExpenseSerializer(serializers.ModelSerializer):
    class Meta: model=TravelExpense; fields='__all__'
class MaintenanceOrderSerializer(serializers.ModelSerializer):
    class Meta: model=MaintenanceOrder; fields='__all__'
class FuelTransactionSerializer(serializers.ModelSerializer):
    class Meta: model=FuelTransaction; fields='__all__'
