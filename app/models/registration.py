from uuid import uuid4

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


from app.database import Base

class Registration(Base):
    __tablename__ = "registrations"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Уникальный идентификатор регистрации"
    )
    first_name = Column(String, nullable=False, comment="Имя")
    last_name = Column(String, nullable=False, comment="Фамилия")
    event_id = Column(
        UUID(as_uuid=True),
        ForeignKey("events.uuid"),
        nullable=False,
        comment="Идентификатор мероприятия"
    )
    seat_id = Column(
        Integer,
        ForeignKey("seats.id"),
        nullable=False,
        comment="Идентификатор места"
    )
    email = Column(String, nullable=False, comment="Почта")
    ticket_id = Column(
        UUID(as_uuid=True),
        default=uuid4,
        comment="Уникальный идентификатор билета"
    )

    event = relationship("Event", back_populates="registrations")
    seat = relationship("Seat", back_populates="registrations")