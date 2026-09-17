# PostgreSQL schema management

This repository treats PostgreSQL as the physical source of truth.

## Migration policy

Django migrations describe and synchronize Django's model state, but they MUST NOT execute schema-changing DDL against PostgreSQL.

All schema changes are versioned separately under `database/ddl/` and applied through the project's controlled PostgreSQL deployment process.

Django migrations that represent physical schema changes use:

```python
migrations.SeparateDatabaseAndState(
    database_operations=[],
    state_operations=[...],
)
```

Therefore:

- `makemigrations` is allowed and expected.
- `migrate` is not the mechanism used to create or alter the physical schema.
- `database_operations` remains empty for schema changes.
- PostgreSQL DDL is reviewed and versioned independently.
- Do not use `--fake` as a substitute for the migration design.

## Required workflow

1. Update Django models.
2. Run `python manage.py makemigrations` to produce the expected Django state.
3. Review the migration and ensure physical schema operations remain in `database_operations=[]`.
4. Create or update the corresponding SQL file under `database/ddl/`.
5. Review SQL against PostgreSQL 16+.
6. Apply the SQL through the controlled database deployment process.
7. Run Django checks and state validation.

The application layer, API and frontend must never be treated as authoritative persistence layers. Operational truth remains in PostgreSQL.
