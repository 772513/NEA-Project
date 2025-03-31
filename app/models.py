from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from flask_login import UserMixin
from hashlib import md5


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    forename: so.Mapped[str] = so.mapped_column(sa.String(64))
    surname: so.Mapped[str] = so.mapped_column(sa.String(64))
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    user_scores: so.WriteOnlyMapped["Score"] = so.relationship(back_populates="user")

    matches: so.WriteOnlyMapped["User"] = so.relationship(
        secondary="score",
        primaryjoin=("score.c.user_id" == id),
        secondaryjoin=("score.c.match_id" == id),
        back_populates="users",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

    def __repr__(self):
        return "<User {}>".format(self.username)

    def get_scores(self):
        return (
            sa.select(Score)
            .join(Score.match)
            .join(Score.user)
            .where(User.id == id)
            .order_by(Match.timestamp.desc())
        )

class Match(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    opponent: so.Mapped[str] = so.mapped_column(sa.String(64))
    location: so.Mapped[str] = so.mapped_column(sa.String(64))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )

    match_scores: so.WriteOnlyMapped["Score"] = so.relationship(back_populates="match")

    users: so.WriteOnlyMapped["Match"] = so.relationship(
        secondary="score",
        primaryjoin=("score.c.match_id" == id),
        secondaryjoin=("score.c.user_id" == id),
        back_populates="matches",
    )

    def __repr__(self):
        return "<Match {} {}>".format(self.location, self.timestamp)


class Score(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    score: so.Mapped[int] = so.mapped_column(sa.Integer)
    turn_number: so.Mapped[int] = so.mapped_column(sa.Integer, index=True)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    match_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Match.id), index=True)

    user: so.WriteOnlyMapped[User] = so.relationship(back_populates="user_scores")
    match: so.WriteOnlyMapped[Match] = so.relationship(back_populates="match_scores")


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
