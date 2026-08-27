import uuid

from sqlalchemy import Column, UUID, String, DateTime, func
from sqlalchemy.orm import relationship

from app.database import Base


class Place(Base):
    __tablename__ = "places"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Уникальный идентификатор площадки"
    )
    name = Column(String, nullable=False, comment="Название площадки")
    city = Column(String, nullable=False, comment="Город")
    address = Column(String, nullable=False, comment="Адрес")
    seats_pattern = Column(
        String,
        nullable=False,
        comment="паттерн мест в формате A1-1000,B1-2000"
    )
    changed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Дата и время последнего изменения площадки"
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Дата и время создания площадки"
    )

    events = relationship("Event", back_populates="place")
