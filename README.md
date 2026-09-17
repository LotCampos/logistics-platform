# Logistics Platform

Enterprise logistics platform for service scheduling, route planning, fleet management, travel expenses, service execution, documents and analytics.

## Stack
- Python 3.12+
- Django 5.2+
- Django REST Framework
- PostgreSQL 16+
- React/Vite frontend (planned integration point)

## Architecture
The platform is intentionally independent from `marketing-platform`. Cross-domain references use UUIDs so Commercial and Master can be integrated later through APIs/events without circular database dependencies.

## Initial setup
1. Create a PostgreSQL database and user.
2. Copy `.env.example` to `.env`.
3. Set `DATABASE_URL`.
4. Create a virtual environment.
5. Install `backend/requirements.txt`.
6. Run `python backend/manage.py migrate`.
7. Run `python backend/manage.py createsuperuser`.
8. Run `python backend/manage.py runserver`.

See `docs/ARCHITECTURE.md` and `docs/POSTGRESQL.md`.
