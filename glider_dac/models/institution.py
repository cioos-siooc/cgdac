from datetime import datetime

from glider_dac.models.shared_db import db

from sqlalchemy import Integer, String, DateTime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class Institution(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.current_timestamp(), nullable=True)
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    def get_id(self):
        return str(self.id)
