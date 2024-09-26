# Starlette App with SQLAlchemy ORM


> This is a simple Starlette app with SQLAlchemy ORM. This example includes the following features:

1. Connection Pooling
2. CRUD Operations (Create, Read, Update, Delete)
3. Caching with Redis (optional)
4. Async support using the databases package.
5. Transaction Handling & Transaction Management using `databases`.
6. Batch Queries and Pagination for performance optimization.
7. Error Handling & Advanced Exception Handling with custom error classes and rollback.
8. Middleware for Dependency Injection of Database Sessions
9. Websockets (optional)
10. Background Tasks (optional)


## Package Requirements

```bash
pip install starlette sqlalchemy databases asyncpg psycopg2 uvicorn
```