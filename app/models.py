from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db


class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    forename: so.Mapped[str] = so.mapped_column(sa.String(64))
    surname: so.Mapped[str] = so.mapped_column(sa.String(64))
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    matches: so.WriteOnlyMapped["Match"] = so.relationship(back_populates="author")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User {}>".format(self.username)


class Match(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    opponent: so.Mapped[str] = so.mapped_column(sa.String(64))
    location: so.Mapped[str] = so.mapped_column(sa.String(64))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates="matches")

    def __repr__(self):
        return '<Match {} {}>'.format(self.location, self.timestamp)