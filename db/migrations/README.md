# Alembic Migration Management

Use Alembic to manage your PostgreSQL schema migrations.

## Commands

```bash
alembic init migrations
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```
