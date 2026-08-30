from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

import uuid

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        comment="Уникальный идентификатор события"
    )
    place_id = Column(
        UUID(as_uuid=True),
        ForeignKey("places.uuid"),
        nullable=False,
        index=True
    )
    name = Column(String, nullable=False, comment="Название мероприятия")
    event_time = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Дата и время начала мероприятия"
    )
    registration_deadline = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="крайний срок регистрации"
    )
    status = Column(String, default="new", comment="Статус события")
    number_of_visitors = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Количество зарегистрированных участников"
    )
    changed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Дата и время последнего изменения"
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Дата и время создания"
    )
    status_changed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата и время последнего изменения статуса"
    )

    place = relationship("Place", back_populates="events")

