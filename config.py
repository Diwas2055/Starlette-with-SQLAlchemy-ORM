# The `databases` package allows for fully async database interactions. We’ll manage transactions using this package.

import databases
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://postgres:docker@localhost:5432/my_db_dev"

# Async Database connection
database = databases.Database(
    DATABASE_URL, min_size=5, max_size=20
)  # Database connection pool size

# min_size=5: Minimum number of connections in the pool.
# max_size=20: Maximum number of connections in the pool.

# MetaData for models
metadata = MetaData()

# Database Engine with Connection Pooling
engine = create_async_engine(
    DATABASE_URL, pool_size=10, max_overflow=5, pool_timeout=30, pool_recycle=1800
)
