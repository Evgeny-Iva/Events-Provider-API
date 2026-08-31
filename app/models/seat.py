from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


from app.database import Base

class Seat(Base):
    __tablename__ = "seats"

    id = Column(
        Integer,
        primary_key=True,
        comment="Уникальный идентификатор места"
    )
    place_id = Column(
        UUID(as_uuid=True),
        ForeignKey("places.uuid"),
        nullable=False,
        comment="Площадка, где будет проходить событие"
    )
    section = Column(String(1), nullable=False, comment="Секция")
    seat_number = Column(Integer, nullable=False, comment="Номер места")
    is_available = Column(Boolean, default=True, comment="Статус места")

    place = relationship("Place", back_populates="seats")
    registrations = relationship("Registration", back_populates="seat")
