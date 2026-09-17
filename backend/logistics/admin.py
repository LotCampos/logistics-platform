from django.contrib import admin
from .models import *
admin.site.register([Vehicle,VehicleMileage,MaintenancePlan,MaintenanceOrder,FuelTransaction,ServiceSchedule,Trip,Route,RouteStop,TravelBudget,TravelExpense,CheckInOut,LogisticsDocument])
