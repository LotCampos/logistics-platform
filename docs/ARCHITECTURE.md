# Architecture

## Domains

- Planning: trips, routes and route stops.
- Scheduling: service appointments and operational status.
- Fleet: vehicles, mileage, maintenance and fuel.
- Expenses: travel budgets and actual expenses.
- Execution: check-in/check-out and service evidence.
- Documents: transactional documents and future PDF generation.
- Analytics: operational and cost KPIs.
- Integrations: future APIs/events with Commercial and Master.

## Integration rule

Do not create direct foreign keys to `marketing-platform`. External entities are represented by UUIDs (`client_id`, `installation_id`, `service_request_id`, `service_catalog_id`, `technician_id`). This keeps the logistics bounded context deployable independently.

## Operational flow

Master Installation → Commercial Service Request → Logistics Service Schedule → Trip → Route/Vehicle → Travel Budget → Execution → Evidence/Report.

## Map provider abstraction

The Route model stores `provider`, `geometry`, `distance_km` and `duration_minutes`. A provider adapter can later implement Mapbox, Google, OSRM or another routing engine without changing logistics business entities.
