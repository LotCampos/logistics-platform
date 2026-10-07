# Logistics CRM — Baseline del Módulo de Logística

Estado: BASELINE FUNCIONAL Y TÉCNICO — NO FROZEN
Versión: 0.1
Fecha: 2026-10-06

## 1. Propósito

Logistics es un sistema operativo para administrar la ejecución logística de servicios de campo.

Pregunta central: ¿qué servicio debe realizarse, dónde, cuándo, con quién, con qué vehículo, por qué ruta y cuánto costará ejecutarlo?

Principio rector: la complejidad debe estar en la arquitectura interna, no en la cantidad de pasos que realiza el usuario.

Logistics no será un segundo CRM comercial ni un ERP logístico. Será una capa operativa especializada, independiente y posteriormente integrable con UI-CADO Comercial.

## 2. Principios arquitectónicos

1. PostgreSQL es Source of Truth.
2. React nunca accede directamente a PostgreSQL.
3. Django/DRF concentra la lógica de aplicación y expone la API.
4. Los datos maestros existentes no se duplican.
5. La operación cotidiana debe requerir pocos pasos.
6. Las entidades internas pueden ser más detalladas que las pantallas.
7. Historial y trazabilidad no deben sacrificarse por simplicidad de interfaz.
8. Estados y reglas críticas se controlan en backend/PostgreSQL.
9. La auditoría es transversal.
10. La arquitectura debe permitir crecer sin obligar a implementar toda la complejidad desde el inicio.

## 3. Límites de dominio

MASTER es fuente de verdad para Client, Contact, Installation, InstallationType y ServiceCatalog. Logistics utiliza sus UUID/referencias y no crea copias maestras.

COMMERCIAL es fuente de verdad para ServiceRequest, Opportunity, Quotation y Agreement. Una ServiceRequest puede generar una o varias programaciones logísticas. Logistics no crea ServiceOrder como duplicado de ServiceRequest.

IDENTITY es fuente de verdad para User. No crear logistics.User, logistics.Driver ni logistics.Technician.

TECH es responsable de la ejecución técnica. Logistics registra traslado, llegada, presencia, check-in, check-out, ubicación, observaciones y evidencia logística. No duplica inspecciones, mediciones, hallazgos, dictámenes ni evidencia técnica.

DOC es responsable del motor documental transversal. Logistics mantiene referencias contextuales.

WORKFLOW y AUDIT son transversales. No crear motores paralelos.

## 4. Flujo operativo simplificado

Servicio → Programar → Asignar recursos → Crear/planificar viaje → Calcular ruta → Presupuestar viáticos → Autorizar cuando corresponda → Ejecutar → Cerrar.

Internamente: ServiceRequest → ServiceSchedule → ServiceAssignment → Trip → Route → RouteStop → TravelBudget → TravelExpense → ServiceExecution.

Una reprogramación no destruye el historial.

## 5. Núcleo transaccional

### ServiceSchedule
Representa cuándo y cómo se programa operativamente un servicio proveniente de Commercial.
Campos conceptuales: service_request_id, client_id, installation_id, service_catalog_id, scheduled_start, scheduled_end, status, notes, version_lock, created_at, updated_at.
NO debe contener como fuente principal trip_id ni vehicle_id. Los recursos se resuelven mediante ServiceAssignment.

### ServiceAssignment
Relación operativa entre programación y recursos.
Campos conceptuales: service_schedule_id, user_id, vehicle_id nullable, trip_id nullable, assigned_at, unassigned_at nullable, status, version_lock.
En interfaz no necesita ser una pantalla independiente. La acción puede ser 'Asignar servicio' y seleccionar responsable, vehículo y viaje.

### Trip
Unidad administrativa/logística de desplazamiento. Campos conceptuales: trip_code, status, planned_start, planned_end, actual_start, actual_end, responsible_user_id, vehicle_id nullable.
Un Trip puede atender varios servicios.

### Route
Recorrido geográfico de un Trip. Contiene trip_id, provider, distance_km, duration_minutes, geometry y calculated_at.
La geometría es derivada/cacheable. La ruta histórica confirmada debe poder reproducirse.

### RouteStop
Punto ordenado del recorrido. No debe asumir que todo punto es una Installation.
Campos conceptuales: route_id, sequence, stop_type, installation_id nullable, service_schedule_id nullable, name/label, latitude/longitude como snapshot cuando sea necesario, planned_arrival, planned_departure, actual_arrival, actual_departure, status, notes.
Tipos iniciales posibles: ORIGIN, SERVICE, DESTINATION, REST, LODGING, FUEL, OTHER. No todos deben habilitarse en el MVP.

## 6. Fleet

Vehicle es maestro de Logistics y contiene identificación y características estables.
VehicleMileage es la historia autoritativa del kilometraje. Vehicle.current_mileage es únicamente estado/cache operativo.
FuelTransaction registra abastecimientos y permitirá obtener litros, importe, kilometraje, costo/km y consumo.
Maintenance se separa en MaintenancePlan, MaintenanceOrder y MaintenanceItem.

## 7. Estado de vehículo

No mezclar estado administrativo con disponibilidad operativa.
Administrativo: ACTIVO, MANTENIMIENTO, FUERA_DE_SERVICIO, BAJA.
Operativo: DISPONIBLE, ASIGNADO, EN_RUTA.
La disponibilidad real se deriva de estado administrativo + asignaciones + conflictos de horario.

## 8. Viáticos

TravelBudget representa presupuesto/autorización logística de un viaje. Conceptualmente: trip_id, status, estimated_amount, authorized_amount, real_amount, checked_amount, settled_amount, requested_by, approved_by, timestamps, version_lock.
La cardinalidad definitiva Trip/TravelBudget queda pendiente de validar contra la política financiera real; no congelar todavía una relación 1:1 si existen ampliaciones o complementos.

TravelExpense representa un gasto individual. Categorías iniciales: GASOLINA, CASETAS, ALIMENTOS, HOSPEDAJE, ESTACIONAMIENTO, TRANSPORTE, IMPREVISTOS, OTROS.
Todo gasto pertenece a un TravelBudget. Los gastos que requieran comprobante deben mantener referencia documental.

## 9. Ejecución logística

ServiceExecution registra salida, llegada, check-in, check-out, coordenadas, hora, observaciones y evidencia logística.
LOGISTICS = movilidad + presencia + logística.
TECH = servicio técnico + inspección + medición + resultado.

## 10. Documentos

No crear LogisticsDocument.
Utilizar DocumentReference con document_id, entity_type, entity_id, document_type, required y context.
DOC mantiene archivo, versión, hash, almacenamiento, metadata y lifecycle.

## 11. Roles

Modelo mínimo: LOGISTICS_MANAGER, LOGISTICS_AUTHORIZER, AUDITOR y READ_ONLY.
No crear roles independientes para planner, dispatcher, fleet manager, expense settlement, field operator o logistics admin.

## 12. Regla de simplicidad operativa

Una función interna no implica una pantalla.
Internamente pueden existir ServiceSchedule, ServiceAssignment, Trip, Route y TravelBudget; la interfaz puede presentar una sola acción 'Programar servicio' que permita seleccionar fecha, responsable y vehículo, crear/asociar viaje, calcular ruta, estimar viáticos y confirmar.

## 13. Dashboard

Es un read model. Indicadores iniciales: servicios de hoy, viajes activos, pendientes, completados, reprogramados, vehículos disponibles, vehículos en mantenimiento, viáticos pendientes y alertas.
Posteriormente: cumplimiento, costo por viaje, costo por servicio, costo/km, km/servicio, presupuesto vs real, utilización vehicular, tiempo estimado vs real e incidencias.

## 14. Mapa y calendario

El mapa es una capacidad, no una entidad maestra. Debe visualizar instalaciones, viajes y paradas, planificar rutas y calcular distancia/duración. Usar adapter MapProvider y no congelar proveedor.

El calendario es una vista de ServiceSchedule. No crear entidad Calendar. Toda modificación debe terminar en operación backend transaccional y auditable.

## 15. API

Base: /api/v1/logistics/
Recursos: service-schedules, service-assignments, trips, routes, route-stops, vehicles, vehicle-mileage, fuel, maintenance, travel-budgets, travel-expenses, service-executions, dashboard y analytics.
Los cambios críticos deben exponerse como comandos: confirm, reschedule, cancel, authorize, start, complete, settle, assign y reassign.

## 16. Arquitectura Django

Capas: models, repositories, services, selectors, dtos, serializers, views, permissions e integrations.
Views no contienen reglas de negocio. Services ejecutan casos de uso y transacciones. Repositories encapsulan persistencia. Selectors optimizan lecturas. Integrations abstraen servicios externos.

## 17. PostgreSQL

Schema recomendado: logistics.
Entidades principales: service_schedules, service_assignments, trips, routes, route_stops, vehicles, vehicle_mileage, fuel_transactions, maintenance_plans, maintenance_orders, maintenance_items, travel_budgets, travel_expenses, service_executions y document_references.
Convenciones: UUID como PK, timestamptz para eventos, numeric para dinero, constraints e índices en PostgreSQL, unique constraints para identificadores operativos y UUID/contratos para referencias cross-domain.
Django migrations serán state-only mediante SeparateDatabaseAndState(database_operations=[], state_operations=[...]). El DDL físico se versionará independientemente.

## 18. Reglas críticas

1. No programar Installation inexistente/inactiva.
2. Validar compatibilidad Client/Installation.
3. No asignar vehículo administrativamente no disponible.
4. Detectar conflictos de vehículo y usuario.
5. No permitir kilometraje descendente sin corrección controlada.
6. Todo gasto pertenece a un TravelBudget.
7. Todo gasto con comprobante obligatorio debe tener referencia documental.
8. No alterar silenciosamente una ruta confirmada.
9. Las reprogramaciones conservan historial.
10. Operaciones críticas son transaccionales.
11. Cambios sensibles quedan auditados.
12. No eliminar físicamente información operacional histórica.
13. Cálculos financieros autoritativos ocurren en backend/PostgreSQL.
14. React nunca es fuente de verdad.

## 19. Modelo mínimo de operación

Para un servicio con tres instalaciones, el usuario debe poder: consultar servicio → seleccionar fecha → seleccionar responsable → seleccionar vehículo → crear viaje → agregar instalaciones → calcular ruta → generar presupuesto → autorizar si corresponde → iniciar → registrar llegadas/salidas → cargar comprobantes → cerrar.

El sistema mantiene internamente el historial y trazabilidad sin obligar al usuario a navegar entre módulos innecesarios.

## 20. Fuera del MVP

Posponer optimización avanzada de rutas, GPS/telemática en tiempo real, app móvil nativa, IA predictiva de mantenimiento, integraciones automáticas de combustible, optimización financiera avanzada, automatizaciones complejas, múltiples roles operativos, workflow paralelo y motor documental paralelo.

## 21. Integración futura con UI-CADO

COMMERCIAL.ServiceRequest → LOGISTICS.ServiceSchedule → LOGISTICS.ServiceAssignment → LOGISTICS.Trip → LOGISTICS.Route/RouteStop → LOGISTICS.TravelBudget → LOGISTICS.ServiceExecution → DOC/AUDIT.

No duplicar Client, Installation, ServiceCatalog, User, ServiceRequest, Quotation ni Agreement.
Una ServiceRequest puede generar múltiples ServiceSchedules. Una Quotation no es un Trip. Un Agreement no es una autorización logística.

## 22. Matriz

| Entidad | Acción | Dominio |
|---|---|---|
| Client / Contact / Installation / ServiceCatalog | REUTILIZAR | MASTER |
| User | REUTILIZAR | IDENTITY |
| ServiceRequest / Quotation / Agreement | REUTILIZAR | COMMERCIAL |
| ServiceSchedule / ServiceAssignment | CREAR | LOGISTICS |
| Trip / Route / RouteStop | CREAR | LOGISTICS |
| Vehicle / VehicleMileage / FuelTransaction | CREAR | LOGISTICS |
| MaintenancePlan / MaintenanceOrder / MaintenanceItem | CREAR | LOGISTICS |
| TravelBudget / TravelExpense | CREAR | LOGISTICS |
| ServiceExecution / DocumentReference | CREAR | LOGISTICS/DOC |
| LogisticsDocument | ELIMINAR | LOGISTICS |
| Calendar como entidad | ELIMINAR | LOGISTICS |
| Driver / Technician como maestros | ELIMINAR | LOGISTICS |
| KPI transaccional | ELIMINAR | ANALYTICS |
| MapProvider | CREAR adapter | INTEGRATION |

## 23. Criterio para FROZEN v1.0

Este baseline no autoriza DDL definitivo.
Antes de congelar deben verificarse: PostgreSQL real, tablas, constraints, índices, ownership, roles, search_path, privileges, DDL actual, contratos de MASTER/COMMERCIAL/IDENTITY, política real de TravelBudget, capacidades de User, necesidad de múltiples participantes por Trip y estrategia definitiva de DocumentReference.

Después de la reconciliación: PostgreSQL → DDL → Django state → API → React, sin rediseño estructural durante la implementación.

## 24. Regla final

Logistics debe sentirse simple para quien lo utiliza.
La arquitectura debe soportar múltiples servicios, instalaciones, reprogramaciones, viajes con múltiples servicios, rutas, vehículos, personal, viáticos, evidencias, historial, auditoría e integración comercial.
La operación cotidiana debe reducirse a: PROGRAMAR → ASIGNAR → VIAJAR → EJECUTAR → CERRAR.

La complejidad técnica existe para proteger la operación, no para hacerla más lenta.