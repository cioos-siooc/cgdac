from datetime import datetime

from glider_dac.models.shared_db import db

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

# this class is used for timestamp storage when running some things
class Timestamp(db.Model):
    id: Mapped[str] = mapped_column(String, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
