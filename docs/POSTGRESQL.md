# PostgreSQL configuration

The application does not create or manage your PostgreSQL server. Configure the database yourself and provide these environment variables:

```env
POSTGRES_DB=logistics_platform
POSTGRES_USER=logistics
POSTGRES_PASSWORD=change-this
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Recommended PostgreSQL version: 16 or newer.

Then run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend/manage.py makemigrations logistics
python backend/manage.py migrate
python backend/manage.py createsuperuser
python backend/manage.py runserver
```

The generated migration should be committed after the first successful local schema generation. Production deployments should use reviewed migrations and never run `makemigrations` automatically.
