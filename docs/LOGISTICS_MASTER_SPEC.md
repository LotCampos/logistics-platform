# Especificación Maestra de Logistics para UI-CADO

Estado: CANDIDATA A CONGELACIÓN — requiere reconciliación final contra el PostgreSQL operativo antes de marcarse FROZEN.
Fecha: 2026-09-21
Repositorios analizados:
- LotCampos/marketing-platform
- LotCampos/logistics-platform

## 0. Decisión arquitectónica

Logistics NO será una segunda arquitectura de UI-CADO ni una copia de MASTER, COMMERCIAL, IDENTITY, TECH, DOC, WORKFLOW o AUDIT.

PostgreSQL continúa siendo Source of Truth. Django/DRF es capa de aplicación y API. React es presentación. Mapas, calendario, PDF y analytics son proyecciones/servicios derivados.

La integración entre repositorios debe ser por contratos de dominio y UUID, no por duplicación de tablas maestras.

## 1. Alcance del dominio

LOGISTICS administra el ciclo físico-operativo necesario para prestar servicios:
1. planificación de servicios;
2. agenda y asignaciones;
3. viajes;
4. rutas y paradas;
5. vehículos;
6. kilometraje, combustible y mantenimiento operativo;
7. presupuestos y gastos de viaje;
8. ejecución logística;
9. evidencias logísticas;
10. expediente operativo y documentos derivados;
11. indicadores operativos.

LOGISTICS no administra:
- clientes maestros;
- instalaciones maestras;
- catálogo maestro de servicios;
- oportunidades;
- cotizaciones;
- contratos;
- usuarios/autenticación;
- workflow transversal;
- auditoría transversal;
- expediente técnico de inspección;
- documentos maestros corporativos fuera de su contexto operativo.

## 2. Límites de dominio

MASTER — REUTILIZAR.
Fuente de verdad para Client, Contact, Installation, InstallationType y ServiceCatalog. Logistics solo conserva UUIDs de referencia y snapshots estrictamente necesarios para histórico, si posteriormente se justifican.

COMMERCIAL — REUTILIZAR / INTEGRAR.
ServiceRequest inicia la necesidad comercial/servicio. Quotation y Agreement permanecen en Commercial. Logistics no crea cotizaciones ni replica solicitudes.

OPERATION — MODIFICAR / DEFINIR COMO DOMINIO DE OPERACIÓN TÉCNICA, NO LOGÍSTICA.
Actualmente está vacío. No mover Fleet/Trips/Expenses a operation sin una decisión arquitectónica posterior. Logistics conserva la responsabilidad de movilidad y recursos logísticos.

TECH — REUTILIZAR.
Debe contener la ejecución técnica de inspección/servicio cuando se defina. Logistics solo registra ejecución logística: traslado, presencia, check-in/out y evidencia logística.

DOC — REUTILIZAR.
Documento físico, archivo, versión, hash, almacenamiento y ciclo documental transversal deben pertenecer a DOC. Logistics tendrá referencias documentales y metadatos contextuales, no un segundo motor documental.

WORKFLOW — REUTILIZAR.
Las transiciones transversales deben centralizarse cuando el módulo workflow esté definido. Mientras tanto, Logistics define estados de dominio y reglas de transición; no crear un motor paralelo de workflow.

AUDIT — REUTILIZAR.
Logs de quién/cuándo/qué cambio deben pertenecer a Audit. Logistics no crea un segundo sistema de auditoría.

IDENTITY — REUTILIZAR.
User es fuente de verdad para identidad. Driver/Technician no deben duplicar usuarios.

## 3. Modelo conceptual

Commercial:
ServiceRequest -> necesidad de servicio.

Logistics:
ServiceSchedule -> programación operativa.
Assignment -> recursos/personas asignados.
Trip -> unidad administrativa de desplazamiento.
Route -> recorrido geográfico de un Trip.
RouteStop -> punto de recorrido.
TravelBudget -> presupuesto del Trip.
TravelExpense -> gasto/comprobación.
ServiceExecution -> presencia/ejecución logística.
EvidenceReference -> referencia a DOC/evidencia.

La cardinalidad no es 1:1:
ServiceRequest 1:N ServiceSchedule.
ServiceSchedule N:1 Installation.
Trip 1:N Route.
Route 1:N RouteStop.
Trip 1:0..1 TravelBudget.
TravelBudget 1:N TravelExpense.
ServiceSchedule 1:0..1 ServiceExecution.

Una reprogramación crea/actualiza una programación según regla definida; nunca destruye el historial operativo.

## 4. Entidades definitivas

Core Logistics:
- ServiceSchedule
- ServiceAssignment
- Trip
- Route
- RouteStop

Fleet:
- Vehicle
- VehicleMileage
- FuelTransaction
- MaintenancePlan
- MaintenanceOrder
- MaintenanceItem

Expenses:
- TravelBudget
- TravelExpense

Execution:
- ServiceExecution
- CheckIn
- CheckOut
- EvidenceReference

Document integration:
- DocumentReference

Analytics:
- ningún modelo transaccional obligatorio; read models/selectors.

Integrations:
- MapRouteResult / provider DTO, no entidad maestra.

Entidades a ELIMINAR del diseño actual:
- LogisticsDocument como sistema documental independiente.
- Driver como maestro duplicado.
- Client, Installation, ServiceCatalog dentro de Logistics.
- Technician como maestro duplicado.

## 5. Relaciones

ServiceSchedule:
- service_request_id nullable UUID
- client_id UUID
- installation_id nullable UUID
- service_catalog_id nullable UUID
- assigned_user_id / assignment relation
- vehicle_id nullable FK a Vehicle
- trip_id nullable UUID según diseño de asignación final

La referencia a Commercial/Master se mantiene por UUID cuando la arquitectura entre schemas/repositorios lo requiera.

Trip:
- responsible_user_id
- vehicle_id
- driver_user_id
- departure/return
- status

Route:
- trip_id
- origin/destination
- provider
- distance/duration
- geometry derivada/cacheable

RouteStop:
- route_id
- sequence
- installation_id
- service_schedule_id
- ETA/arrival/departure
- coordinates snapshot cuando sea necesario para preservar el cálculo histórico.

## 6. Estados y transiciones

ServiceSchedule:
PROGRAMADO -> CONFIRMADO -> EN_RUTA -> EN_SITIO -> EN_EJECUCION -> COMPLETADO.
PROGRAMADO/CONFIRMADO -> REPROGRAMADO.
PROGRAMADO/CONFIRMADO -> CANCELADO.
No se permite volver a estados anteriores salvo una transición explícita de corrección administrativa.

Trip:
BORRADOR -> PENDIENTE_AUTORIZACION -> AUTORIZADO -> ACTIVO -> COMPLETADO.
BORRADOR/PENDIENTE_AUTORIZACION -> CANCELADO.
Un viaje iniciado no puede volver a BORRADOR.

TravelBudget:
BORRADOR -> PENDIENTE_AUTORIZACION -> AUTORIZADO -> EN_CURSO -> COMPLETADO -> LIQUIDADO.
Rechazo debe quedar auditado; no borrar el presupuesto anterior.

Vehicle:
DISPONIBLE -> ASIGNADO -> EN_RUTA -> DISPONIBLE.
DISPONIBLE/ASIGNADO -> MANTENIMIENTO.
MANTENIMIENTO -> DISPONIBLE/FUERA_DE_SERVICIO.
FUERA_DE_SERVICIO -> BAJA.

RouteStop:
PENDIENTE -> EN_RUTA/ARRIBO -> COMPLETADA.
PENDIENTE -> OMITIDA solo con motivo obligatorio.

## 7. Reglas de negocio

1. No se programa un servicio sobre una Installation inexistente/inactiva.
2. ServiceSchedule debe validar que client/installación sean compatibles.
3. No se asigna un vehículo en mantenimiento, fuera de servicio o baja.
4. No se permiten solapamientos de vehículo en intervalos incompatibles.
5. No se permite doble asignación incompatible de usuario/driver.
6. La ruta debe poder reproducir su cálculo histórico.
7. RouteStop debe mantener orden único dentro de Route.
8. El kilometraje no puede retroceder sin una corrección auditada.
9. Un gasto requiere pertenecer a un TravelBudget.
10. Gastos que requieran comprobante no pueden liquidarse sin referencia documental válida.
11. El monto liquidado debe reconciliar presupuesto/autorización según política.
12. Los estados se cambian mediante servicios de aplicación, no mediante edición directa desde React.
13. Las operaciones críticas usan transacciones.
14. Concurrencia optimista mediante version_lock cuando aplique.
15. No se elimina físicamente información operacional que forme parte del historial.
16. Los cálculos financieros se hacen en backend/PostgreSQL, nunca solo en frontend.
17. Los KPIs no son Source of Truth.

## 8. Roles y segregación

Roles mínimos funcionales:
- LOGISTICS_ADMIN
- LOGISTICS_PLANNER
- FLEET_MANAGER
- TRAVEL_AUTHORIZER
- EXPENSE_SETTLEMENT
- DISPATCHER/COORDINATOR
- FIELD_OPERATOR
- AUDITOR/READ_ONLY

Segregación:
- quien solicita/programa no debe aprobar su propio presupuesto cuando la política exija separación;
- quien registra un gasto no debe modificar la evidencia aprobatoria de ese gasto;
- quien ejecuta servicio no debe alterar retrospectivamente la programación aprobada sin permiso;
- Fleet Manager administra disponibilidad/mantenimiento, no aprueba gastos financieros por defecto;
- Auditor es de consulta/auditoría.

La identidad real proviene de identity.User.

## 9. Modelo PostgreSQL

Schema lógico recomendado: logistics.

Tablas principales:
logistics.service_schedules
logistics.service_assignments
logistics.trips
logistics.routes
logistics.route_stops
logistics.vehicles
logistics.vehicle_mileage
logistics.fuel_transactions
logistics.maintenance_plans
logistics.maintenance_orders
logistics.maintenance_items
logistics.travel_budgets
logistics.travel_expenses
logistics.service_executions
logistics.check_ins
logistics.check_outs
logistics.document_references

Convenciones:
- UUID como PK;
- timestamptz para eventos;
- numeric para dinero;
- constraints en PostgreSQL;
- índices por estado, fechas, vehículo, instalación, trip y schedule;
- unique constraints para números operativos;
- FK internas cuando pertenecen al mismo dominio;
- referencias cross-domain por UUID donde la separación de schemas/repositorios lo requiera.

DDL físico se versiona en database/ddl/.
Django migrations son state-only con SeparateDatabaseAndState(database_operations=[]).

## 10. Arquitectura Django

App:
backend/logistics/

Capas:
models/
repositories/
services/
selectors/
dtos/
serializers/
views/
urls/
permissions/
integrations/

Views no contienen reglas de negocio.
Serializers validan forma de entrada/salida, no orquestación.
Services ejecutan casos de uso y transacciones.
Repositories encapsulan persistencia.
Selectors construyen lecturas optimizadas/read models.
Integrations abstraen mapas y otros proveedores.

## 11. Repositories / Services / Selectors

Repositories:
- ServiceScheduleRepository
- AssignmentRepository
- TripRepository
- RouteRepository
- RouteStopRepository
- VehicleRepository
- VehicleMileageRepository
- FuelTransactionRepository
- MaintenanceRepository
- TravelBudgetRepository
- TravelExpenseRepository
- ServiceExecutionRepository
- DocumentReferenceRepository

Services:
- ScheduleService
- AssignmentService
- TripLifecycleService
- RoutePlanningService
- FleetService
- MileageService
- FuelService
- MaintenanceService
- TravelBudgetService
- TravelExpenseService
- ExecutionService
- DocumentReferenceService

Selectors:
- DashboardSelector
- ServiceScheduleSelector
- FleetSelector
- RouteSelector
- TravelExpenseSelector
- AnalyticsSelector

No CRUD genérico como sustituto de casos de uso críticos.

## 12. API contracts

Versionar API: /api/v1/logistics/

Recursos:
GET/POST /service-schedules
GET/PATCH /service-schedules/{id}
POST /service-schedules/{id}/confirm
POST /service-schedules/{id}/reschedule
POST /service-schedules/{id}/cancel

GET/POST /trips
POST /trips/{id}/authorize
POST /trips/{id}/start
POST /trips/{id}/complete

GET/POST /routes
POST /routes/plan
GET /routes/{id}/stops

GET/POST /vehicles
GET/PATCH /vehicles/{id}
GET/POST /vehicles/{id}/mileage
GET/POST /vehicles/{id}/fuel
GET/POST /vehicles/{id}/maintenance

GET/POST /travel-budgets
POST /travel-budgets/{id}/submit
POST /travel-budgets/{id}/authorize
POST /travel-budgets/{id}/settle

GET/POST /travel-expenses

GET /dashboard
GET /analytics

Las respuestas deben exponer IDs, estado, version_lock, timestamps y referencias necesarias para UI.

## 13. Arquitectura React

Separar:
frontend/src/modules/logistics/
  dashboard/
  planning/
  calendar/
  routes/
  fleet/
  expenses/
  execution/
  documents/

Infraestructura:
frontend/src/infrastructure/api/
frontend/src/infrastructure/maps/
frontend/src/infrastructure/auth/

Hooks y estado de servidor separados del estado visual.

React nunca escribe PostgreSQL.
React nunca calcula como autoridad totales financieros, disponibilidad definitiva o estados.

## 14. Dashboard

Debe ser un read model operativo.

KPIs:
- servicios hoy;
- viajes activos;
- flotilla disponible;
- viáticos pendientes;
- servicios retrasados;
- mantenimientos próximos;
- documentos próximos a vencer.

Widgets:
- mapa operativo;
- agenda;
- estado de flotilla;
- alertas;
- costo logístico acumulado;
- variación presupuesto vs gasto.

Los valores actuales del dashboard demo NO son datos reales y deben eliminarse al conectar API.

## 15. Mapa

Crear adapter:
MapProvider.

Debe soportar inicialmente:
- geocodificación;
- cálculo de ruta;
- distancia;
- duración;
- geometría;
- waypoints.

La instalación se obtiene desde MASTER/contrato API, no se replica.

El mapa puede cachear resultados de routing, pero la ruta histórica usada por una operación debe persistirse.

Proveedor inicial: desacoplado. No congelar Mapbox/Google/OSRM como dependencia de dominio.

## 16. Scheduler

Scheduler es la vista operativa de ServiceSchedule.

Funciones:
- día/semana/mes;
- disponibilidad;
- conflictos;
- filtros por cliente, instalación, servicio, técnico, vehículo y estado;
- drag/drop solo si termina en una operación backend transaccional;
- reprogramación auditada.

No crear una entidad Calendar independiente.

## 17. Fleet

Vehicle es maestro de Logistics.

Debe cubrir:
- identificación;
- placas;
- VIN;
- tipo;
- combustible;
- capacidad;
- estado;
- kilometraje actual.

Histórico separado:
- mileage;
- fuel;
- maintenance.

La disponibilidad real se determina por reglas y asignaciones, no por un booleano manual únicamente.

## 18. Trips / Routes

Trip = unidad administrativa/logística de desplazamiento.

Route = recorrido geográfico de Trip.

RouteStop = parada ordenada.

Un Trip puede tener más de una Route cuando la operación lo justifique.

No hacer Route y Trip equivalentes.

La optimización automática de paradas debe ser una función explícita y no alterar silenciosamente el orden confirmado.

## 19. Expenses / Viáticos

TravelBudget = autorización/presupuesto del viaje.

TravelExpense = comprobación individual.

Categorías iniciales:
GASOLINA, CASETAS, ALIMENTOS, HOSPEDAJE, ESTACIONAMIENTO, TRANSPORTE, IMPREVISTOS, OTROS.

Separar:
estimado;
autorizado;
real;
comprobado;
liquidado.

No utilizar un único total editable.

La integración con Commercial para reflejar viáticos en una cotización pertenece a Commercial; Logistics consume la consecuencia operativa cuando corresponda.

## 20. Execution / Evidence

Logistics registra:
- salida;
- llegada;
- check-in;
- check-out;
- coordenadas de presencia;
- observaciones;
- evidencia logística.

La evidencia técnica de una inspección pertenece a TECH/operación técnica.

No duplicar expedientes técnicos.

## 21. Documents

ELIMINAR LogisticsDocument como motor documental independiente.

CREAR DocumentReference en Logistics.

DOC debe ser responsable de:
- archivo;
- versión;
- hash;
- almacenamiento;
- metadata documental;
- lifecycle documental.

Logistics conserva:
- tipo contextual;
- entity_id;
- relación con Trip/Expense/ServiceSchedule/etc.;
- obligatoriedad contextual.

PDF:
- Logistics solicita generación;
- DOC/document service materializa el documento;
- el resultado se referencia desde Logistics.

## 22. Analytics

No crear tablas transaccionales para KPIs salvo read models materializados cuando exista necesidad de rendimiento.

Indicadores:
- servicios programados/completados/reprogramados/cancelados;
- cumplimiento;
- costo por viaje;
- costo por servicio;
- costo/km;
- km/servicio;
- consumo de combustible;
- utilización de vehículos;
- presupuesto vs real;
- tiempo de ejecución;
- incidencias;
- utilización de técnicos/operadores.

Todos deben derivarse de datos persistidos.

## 23. Integración con Commercial

Flujo:
COMMERCIAL.ServiceRequest
 -> LOGISTICS.ServiceSchedule
 -> LOGISTICS.Assignment
 -> LOGISTICS.Trip
 -> LOGISTICS.Route/RouteStop
 -> LOGISTICS.TravelBudget
 -> LOGISTICS.Execution
 -> DOC/AUDIT.

ServiceRequest no se copia.

Una ServiceRequest puede originar múltiples ServiceSchedules.

Una Quotation no es un Trip.

Un Agreement no es autorización logística.

Cuando Commercial requiera conocer costo logístico, consultar API/read model de Logistics; no duplicar costos como fuente independiente en Commercial salvo un snapshot contractual explícito.

## 24. Auditoría

AUDIT es transversal.

Debe registrar:
- creación;
- cambio de estado;
- autorización;
- cancelación;
- reprogramación;
- modificación de presupuesto;
- modificación de gastos;
- asignación/reasignación;
- cambios críticos de vehículo;
- correcciones de kilometraje;
- documentos asociados.

Logistics no crea audit tables paralelas.

## 25. Plan de implementación

FASE 0 — arquitectura y reconciliación:
- comparar PostgreSQL real contra modelos;
- cerrar contratos cross-domain;
- cerrar constraints;
- congelar esta especificación.

FASE 1 — foundation:
- app logistics;
- schemas/DDL;
- repositories;
- services;
- selectors;
- permissions;
- API base.

FASE 2 — Fleet:
- vehicles;
- mileage;
- fuel;
- maintenance.

FASE 3 — Scheduling:
- ServiceSchedule;
- assignments;
- calendar;
- conflict detection.

FASE 4 — Trips/Routes:
- Trip;
- Route;
- RouteStop;
- map adapter.

FASE 5 — Expenses:
- TravelBudget;
- TravelExpense;
- authorization;
- settlement;
- document references.

FASE 6 — Execution:
- check-in/out;
- evidence references;
- operational completion.

FASE 7 — Documents:
- integración DOC;
- PDF;
- expediente.

FASE 8 — Analytics:
- dashboard real;
- selectors;
- KPIs.

FASE 9 — Commercial integration:
- eventos/commands/queries;
- service request -> schedule;
- snapshots/logística comercial donde proceda.

FASE 10 — hardening:
- permissions;
- audit;
- concurrency;
- indexes;
- performance;
- observability;
- tests.

## 26. Qué NO se debe implementar

NO crear:
- logistics.Client;
- logistics.Installation;
- logistics.ServiceCatalog;
- logistics.User;
- logistics.Driver como maestro;
- logistics.Technician como maestro;
- LogisticsDocument como segundo DOC;
- Calendar como entidad maestra;
- KPI tables innecesarias;
- Route como sustituto de Trip;
- Trip como sustituto de ServiceSchedule;
- cotizaciones dentro de Logistics;
- contratos dentro de Logistics;
- workflow engine paralelo;
- audit engine paralelo;
- frontend con acceso directo a PostgreSQL;
- reglas financieras críticas exclusivamente en React;
- geometría de mapas como Source of Truth;
- duplicación de datos maestros sin una razón histórica explícita.

## Matriz REUTILIZAR / CREAR / MODIFICAR / ELIMINAR / POSPONER

| Propuesta | Acción | Dominio |
|---|---|---|
| Client | REUTILIZAR | master |
| Contact | REUTILIZAR | master |
| Installation | REUTILIZAR | master |
| InstallationType | REUTILIZAR | master |
| ServiceCatalog | REUTILIZAR | master |
| User | REUTILIZAR | identity |
| ServiceRequest | REUTILIZAR | commercial |
| Quotation | REUTILIZAR | commercial |
| Agreement | REUTILIZAR | commercial |
| ServiceSchedule | CREAR | logistics |
| ServiceAssignment | CREAR | logistics |
| Vehicle | CREAR | logistics |
| VehicleMileage | CREAR | logistics |
| FuelTransaction | CREAR | logistics |
| MaintenancePlan | CREAR | logistics |
| MaintenanceOrder | CREAR | logistics |
| MaintenanceItem | CREAR | logistics |
| Trip | CREAR | logistics |
| Route | CREAR | logistics |
| RouteStop | CREAR | logistics |
| TravelBudget | CREAR | logistics |
| TravelExpense | CREAR | logistics |
| ServiceExecution | CREAR | logistics |
| CheckIn/CheckOut | CREAR | logistics |
| EvidenceReference | CREAR | logistics/DOC |
| DocumentReference | CREAR | logistics + doc |
| LogisticsDocument | ELIMINAR | logistics |
| Driver master | ELIMINAR | logistics |
| Calendar entity | ELIMINAR | logistics |
| KPI entity | ELIMINAR salvo read-model justificado | analytics |
| operation | MODIFICAR/RESERVAR para operación técnica | operation |
| tech | REUTILIZAR | technical |
| doc | REUTILIZAR | transversal |
| workflow | REUTILIZAR | transversal |
| audit | REUTILIZAR | transversal |
| map provider | CREAR adapter | integration |
| PDF engine | REUTILIZAR DOC / MODIFICAR contrato | doc |
| Commercial -> Logistics | CREAR integración contractual | cross-domain |
| Optimización automática de rutas | POSPONER | logistics |
| Telemática/GPS vehicular en tiempo real | POSPONER | logistics |
| App móvil nativa | POSPONER | frontend/mobile |
| IA predictiva de mantenimiento | POSPONER | analytics |
| Optimización financiera avanzada | POSPONER | analytics |
| Integraciones externas de combustible | POSPONER | integration |

## Hallazgos de la auditoría actual

1. marketing-platform ya contiene una separación conceptual correcta entre MASTER y COMMERCIAL.
2. ServiceRequest usa UUIDs para client, installation y service catalog; esto favorece la integración sin duplicar maestros.
3. Commercial ya dispone de repositories y application services; Logistics debe seguir el mismo patrón.
4. core ya define ApplicationService y UnitOfWork; Logistics debe reutilizarlos.
5. identity.User ya existe; no debe crearse otro usuario/conductor maestro.
6. operation, tech, doc, workflow y audit actualmente están prácticamente vacíos en models.py; por tanto sus límites deben quedar definidos ahora, pero no se debe asumir que ya contienen capacidades no implementadas.
7. logistics-platform actual sí contiene un modelo monolítico preliminar que mezcla logística, documentos y ejecución; debe tratarse como baseline de exploración, no como arquitectura congelada.
8. LogisticsDocument debe retirarse como entidad documental autónoma.
9. El modelo actual de RouteStop duplica coordenadas; eso solo debe permanecer como snapshot histórico cuando exista una justificación.
10. TravelBudget actualmente OneToOne con Trip es demasiado restrictivo para congelarlo sin análisis de política; debe conservarse como decisión pendiente si un viaje puede tener ampliaciones/versiones de presupuesto.
11. Vehicle.current_mileage no debe ser la única fuente histórica; VehicleMileage es la historia.
12. MaintenanceOrder necesita MaintenanceItem antes de considerarse cerrado.
13. ServiceSchedule no debe depender de una FK directa a User/Installation cross-domain si eso rompe el boundary; utilizar contratos/UUID según la topología final.
14. El frontend actual es un shell visual con datos demo y NO representa todavía contratos de API reales.
15. La política PostgreSQL del nuevo logistics-platform ya establece DDL separado y migrations state-only.

## Bloqueador de congelación

La revisión de GitHub fue realizada. La consulta directa al proyecto PostgreSQL mediante el conector disponible falló durante esta revisión, por lo que NO se declara aquí que el esquema físico PostgreSQL actual haya sido reconciliado tabla por tabla.

Antes de marcar esta especificación como FROZEN se debe ejecutar:
- inventario real de schemas/tables/constraints/indexes;
- comparación contra marketing-platform;
- comparación contra database/ddl de logistics-platform;
- identificación de tablas existentes que ya cubran alguno de estos conceptos;
- revisión de roles PostgreSQL;
- verificación de search_path;
- verificación de ownership/privileges;
- reconciliación de nombres físicos.

Hasta completar esa etapa, este documento es la BASE MAESTRA DE DISEÑO y cualquier implementación nueva debe respetarlo, pero no debe considerarse autorización para crear DDL definitivo.
