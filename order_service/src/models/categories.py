from typing import Optional

from typing_extensions import Annotated
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.base_models.base_classes import Base, IDMixin, NameMixin

parent_fk = Annotated[int, mapped_column(ForeignKey('categories.id'))]


class Category(Base, IDMixin, NameMixin):
    __tablename__ = 'categories'

    parent_id: Mapped[Optional[parent_fk]]
    level: Mapped[int] = mapped_column(default=0)  # Уровень вложенности (0 - корень)

    children: Mapped[list["Category"]] = relationship(
        back_populates="parent",
        remote_side="Category.parent_id"
    )

    parent: Mapped[Optional["Category"]] = relationship(
        back_populates="children",
        remote_side="Category.id"
    )

    products: Mapped[Optional[list["Product"]]] = relationship(back_populates="category")
