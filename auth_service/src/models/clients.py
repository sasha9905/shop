from typing import Optional

from sqlalchemy.orm import relationship, Mapped

from src.base_models.base_classes import Base, IDMixin, NameMixin


class Client(Base, IDMixin, NameMixin):
    __tablename__ = 'clients'

    address: Mapped[str]

    orders: Mapped[Optional[list["Order"]]] = relationship(back_populates="client")
