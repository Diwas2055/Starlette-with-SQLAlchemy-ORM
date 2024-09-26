# SQLAlchemy ORM supports mapping Python classes to database tables. Relationships, indexes, and constraints are defined here.

from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, relationship, declared_attr
from sqlalchemy.sql import func
from sqlalchemy import event

Base = declarative_base()


class TimestampMixin(object):
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True)

    addresses = relationship(
        "Address", back_populates="user", cascade="all, delete-orphan"
    )


class Address(Base, TimestampMixin):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)

    user = relationship("User", back_populates="addresses")


@event.listens_for(User, "before_insert")
def receive_before_insert(mapper, connection, target):
    target.created_at = datetime.datetime.now()


@event.listens_for(User, "before_update")
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.datetime.now()


# Define indexes for performance optimization
Index("ix_user_email", User.email, unique=True)
