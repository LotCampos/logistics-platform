from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    """Django state-only migration.

    PostgreSQL DDL is intentionally excluded. The physical schema is managed
    by versioned SQL under database/ddl/.
    """

    initial = True

    dependencies = []

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="Vehicle",
                    fields=[
                        ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        ("updated_at", models.DateTimeField(auto_now=True)),
                        ("unit_number", models.CharField(max_length=30, unique=True)),
                        ("plates", models.CharField(max_length=20, unique=True)),
                        ("brand", models.CharField(max_length=80)),
                        ("model", models.CharField(max_length=80)),
                        ("year", models.PositiveIntegerField()),
                        ("vin", models.CharField(blank=True, max_length=40)),
                        ("vehicle_type", models.CharField(max_length=50)),
                        ("fuel_type", models.CharField(max_length=30)),
                        ("current_mileage", models.DecimalField(decimal_places=1, default=0, max_digits=12)),
                        ("status", models.CharField(choices=[("AVAILABLE", "Disponible"), ("ASSIGNED", "Asignado"), ("ROUTE", "En ruta"), ("MAINTENANCE", "Mantenimiento"), ("OUT", "Fuera de servicio"), ("RETIRED", "Baja")], default="AVAILABLE", max_length=20)),
                    ],
                ),
            ],
        ),
    ]
