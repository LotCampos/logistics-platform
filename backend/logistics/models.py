from django.db import models
from django.contrib.auth import get_user_model
import uuid

User=get_user_model()
class Base(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: abstract=True

class Vehicle(Base):
    class Status(models.TextChoices):
        AVAILABLE='AVAILABLE','Disponible'; ASSIGNED='ASSIGNED','Asignado'; ROUTE='ROUTE','En ruta'; MAINTENANCE='MAINTENANCE','Mantenimiento'; OUT='OUT','Fuera de servicio'; RETIRED='RETIRED','Baja'
    unit_number=models.CharField(max_length=30,unique=True); plates=models.CharField(max_length=20,unique=True); brand=models.CharField(max_length=80); model=models.CharField(max_length=80); year=models.PositiveIntegerField(); vin=models.CharField(max_length=40,blank=True); vehicle_type=models.CharField(max_length=50); fuel_type=models.CharField(max_length=30); current_mileage=models.DecimalField(max_digits=12,decimal_places=1,default=0); status=models.CharField(max_length=20,choices=Status.choices,default=Status.AVAILABLE)

class VehicleMileage(Base):
    vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE,related_name='mileage_records'); recorded_at=models.DateTimeField(); mileage=models.DecimalField(max_digits=12,decimal_places=1); source=models.CharField(max_length=40); notes=models.TextField(blank=True); recorded_by=models.ForeignKey(User,null=True,on_delete=models.SET_NULL)

class MaintenancePlan(Base):
    vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE,related_name='maintenance_plans'); name=models.CharField(max_length=120); interval_km=models.PositiveIntegerField(null=True,blank=True); interval_days=models.PositiveIntegerField(null=True,blank=True); active=models.BooleanField(default=True)

class MaintenanceOrder(Base):
    class Status(models.TextChoices): OPEN='OPEN','Abierta'; PROGRESS='PROGRESS','En proceso'; DONE='DONE','Completada'; CANCELLED='CANCELLED','Cancelada'
    vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE,related_name='maintenance_orders'); plan=models.ForeignKey(MaintenancePlan,null=True,blank=True,on_delete=models.SET_NULL); scheduled_at=models.DateTimeField(); mileage=models.DecimalField(max_digits=12,decimal_places=1,null=True,blank=True); description=models.TextField(); cost=models.DecimalField(max_digits=12,decimal_places=2,default=0); status=models.CharField(max_length=20,choices=Status.choices,default=Status.OPEN)

class FuelTransaction(Base):
    vehicle=models.ForeignKey(Vehicle,on_delete=models.PROTECT,related_name='fuel_transactions'); occurred_at=models.DateTimeField(); station=models.CharField(max_length=160); liters=models.DecimalField(max_digits=10,decimal_places=3); price_per_liter=models.DecimalField(max_digits=10,decimal_places=2); total=models.DecimalField(max_digits=12,decimal_places=2); mileage=models.DecimalField(max_digits=12,decimal_places=1); receipt_number=models.CharField(max_length=80,blank=True)

class ServiceSchedule(Base):
    class Status(models.TextChoices): SCHEDULED='SCHEDULED','Programado'; CONFIRMED='CONFIRMED','Confirmado'; ROUTE='ROUTE','En ruta'; SITE='SITE','En sitio'; EXECUTION='EXECUTION','En ejecución'; COMPLETED='COMPLETED','Completado'; RESCHEDULED='RESCHEDULED','Reprogramado'; CANCELLED='CANCELLED','Cancelado'
    service_request_id=models.UUIDField(null=True,blank=True); client_id=models.UUIDField(); installation_id=models.UUIDField(null=True,blank=True); service_catalog_id=models.UUIDField(null=True,blank=True); scheduled_start=models.DateTimeField(); estimated_minutes=models.PositiveIntegerField(default=60); priority=models.PositiveSmallIntegerField(default=3); technician_id=models.UUIDField(null=True,blank=True); vehicle=models.ForeignKey(Vehicle,null=True,blank=True,on_delete=models.SET_NULL); status=models.CharField(max_length=20,choices=Status.choices,default=Status.SCHEDULED); notes=models.TextField(blank=True)

class Trip(Base):
    class Status(models.TextChoices): DRAFT='DRAFT','Borrador'; AUTHORIZED='AUTHORIZED','Autorizado'; ACTIVE='ACTIVE','Activo'; COMPLETED='COMPLETED','Completado'; CANCELLED='CANCELLED','Cancelado'
    trip_number=models.CharField(max_length=40,unique=True); responsible_id=models.UUIDField(null=True,blank=True); vehicle=models.ForeignKey(Vehicle,null=True,blank=True,on_delete=models.SET_NULL); driver_id=models.UUIDField(null=True,blank=True); departure_at=models.DateTimeField(); return_at=models.DateTimeField(null=True,blank=True); origin=models.CharField(max_length=255); destination=models.CharField(max_length=255); status=models.CharField(max_length=20,choices=Status.choices,default=Status.DRAFT)

class Route(Base):
    trip=models.ForeignKey(Trip,on_delete=models.CASCADE,related_name='routes'); origin=models.CharField(max_length=255); destination=models.CharField(max_length=255); distance_km=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True); duration_minutes=models.PositiveIntegerField(null=True,blank=True); provider=models.CharField(max_length=50,default='abstract'); geometry=models.JSONField(null=True,blank=True)

class RouteStop(Base):
    class Status(models.TextChoices): PENDING='PENDING','Pendiente'; ARRIVED='ARRIVED','Llegó'; COMPLETED='COMPLETED','Completada'; SKIPPED='SKIPPED','Omitida'
    route=models.ForeignKey(Route,on_delete=models.CASCADE,related_name='stops'); installation_id=models.UUIDField(null=True,blank=True); service_schedule=models.ForeignKey(ServiceSchedule,null=True,blank=True,on_delete=models.SET_NULL); stop_order=models.PositiveIntegerField(); latitude=models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True); longitude=models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True); eta=models.DateTimeField(null=True,blank=True); status=models.CharField(max_length=20,choices=Status.choices,default=Status.PENDING)
    class Meta: ordering=['stop_order']; unique_together=[('route','stop_order')]

class TravelBudget(Base):
    class Status(models.TextChoices): DRAFT='DRAFT','Borrador'; PENDING='PENDING','Pendiente autorización'; AUTHORIZED='AUTHORIZED','Autorizado'; ACTIVE='ACTIVE','En curso'; COMPLETED='COMPLETED','Completado'; SETTLED='SETTLED','Liquidado'
    trip=models.OneToOneField(Trip,on_delete=models.CASCADE,related_name='travel_budget'); currency=models.CharField(max_length=3,default='MXN'); total_budget=models.DecimalField(max_digits=14,decimal_places=2,default=0); authorized_amount=models.DecimalField(max_digits=14,decimal_places=2,null=True,blank=True); status=models.CharField(max_length=20,choices=Status.choices,default=Status.DRAFT)

class TravelExpense(Base):
    class Category(models.TextChoices): FUEL='FUEL','Gasolina'; TOLL='TOLL','Casetas'; MEAL='MEAL','Alimentos'; LODGING='LODGING','Hospedaje'; PARKING='PARKING','Estacionamiento'; TRANSPORT='TRANSPORT','Transporte'; CONTINGENCY='CONTINGENCY','Imprevistos'; OTHER='OTHER','Otros'
    budget=models.ForeignKey(TravelBudget,on_delete=models.CASCADE,related_name='expenses'); category=models.CharField(max_length=20,choices=Category.choices); concept=models.CharField(max_length=255); estimated=models.DecimalField(max_digits=12,decimal_places=2,default=0); actual=models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True); receipt_required=models.BooleanField(default=True); receipt_file=models.FileField(upload_to='receipts/%Y/%m/',null=True,blank=True); occurred_at=models.DateTimeField(null=True,blank=True)

class CheckInOut(Base):
    service_schedule=models.OneToOneField(ServiceSchedule,on_delete=models.CASCADE,related_name='execution'); check_in_at=models.DateTimeField(null=True,blank=True); check_in_lat=models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True); check_in_lng=models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True); check_out_at=models.DateTimeField(null=True,blank=True); check_out_lat=models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True); check_out_lng=models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True); observations=models.TextField(blank=True)

class LogisticsDocument(Base):
    class Type(models.TextChoices): TRAVEL_ORDER='TRAVEL_ORDER','Orden de viaje'; BUDGET='BUDGET','Presupuesto de viáticos'; RECEIPT='RECEIPT','Comprobante'; INVOICE='INVOICE','Factura'; EVIDENCE='EVIDENCE','Evidencia'; REPORT='REPORT','Reporte de viaje'; VEHICLE='VEHICLE','Documento vehicular'; MAINTENANCE='MAINTENANCE','Mantenimiento'
    document_type=models.CharField(max_length=20,choices=Type.choices); entity_type=models.CharField(max_length=50); entity_id=models.UUIDField(); file=models.FileField(upload_to='documents/%Y/%m/'); version=models.PositiveIntegerField(default=1); sha256=models.CharField(max_length=64,blank=True); uploaded_by=models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
