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

    # relationship with Score (intermediary table between User and Match)
    user_scores: so.Mapped["Score"] = so.relationship("Score", back_populates="user")

    # relationship with Match via Score
    matches: so.Mapped["Match"] = so.relationship(
        "Match",
        # defines a many-to-many relationship, where the relationship is stored in a
        # separate table (Score)
        secondary="score",
        # ensures that both sides of the relationship are synchronised, so that changes
        # on one side will automatically reflect on the other side
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

    def get_all_scores(self):
        query = (
            sa.select(Score)
            .join(Score.match)
            .join(Score.user)
            .where(Score.user_id == self.id)
            .order_by(Match.timestamp.desc())
        )

        result = db.session.execute(query).scalars().all()

        return result

    def get_score_from_id(self, id):
        return sa.select(Score).where(Score.id == id)

    def remove_score(self, score):
        if score in self.get_all_scores():
            db.session.delete(score)
            db.session.commit()


class Match(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    opponent: so.Mapped[str] = so.mapped_column(sa.String(64))
    location: so.Mapped[str] = so.mapped_column(sa.String(64))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )

    match_scores: so.Mapped["Score"] = so.relationship(
        "Score", back_populates="match", cascade="all, delete"
    )

    # relationship with User via Score
    users: so.Mapped["User"] = so.relationship(
        "User",
        secondary="score",
        back_populates="matches",
    )

    def __repr__(self):
        return "<Match {} {}>".format(self.location, self.timestamp)

    def get_scores(self):
        return (
            sa.select(Score)
            .join(Score.match)
            .join(Score.user)
            .where(Score.match_id == self.id)
            .order_by(Score.id)
        )


class Score(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    score: so.Mapped[int] = so.mapped_column(sa.Integer)
    turn_number: so.Mapped[int] = so.mapped_column(sa.Integer, index=True)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    match_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Match.id), index=True)

    user: so.Mapped[User] = so.relationship(back_populates="user_scores")
    match: so.Mapped[Match] = so.relationship(back_populates="match_scores")


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
