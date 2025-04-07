from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    IntegerField,
    DateField,
)
from wtforms.validators import (
    ValidationError,
    DataRequired,
    Email,
    EqualTo,
    NumberRange,
    Optional,
)
import sqlalchemy as sa
from app import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    forename = StringField("Forename", validators=[DataRequired()])
    surname = StringField("Surname", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password_check = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError("Please use a different username.")


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(
                sa.select(User).where(User.username == username.data)
            )
            if user is not None:
                raise ValidationError("Please use a different username.")


class CRMatchForm(FlaskForm):
    opponent = StringField("Opponent", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    date = StringField("Date (YYYY-MM-DD HH:MM)", validators=[DataRequired()])
    submit = SubmitField("Save Match")


class AddScoreForm(FlaskForm):
    score = IntegerField("Add Score", validators=[DataRequired()])
    submit = SubmitField("Enter")


class EditScoresForm(FlaskForm):
    turn_1 = IntegerField("Turn 1", validators=[Optional(), NumberRange(min=0, max=27)])
    turn_2 = IntegerField("Turn 2", validators=[Optional(), NumberRange(min=0, max=27)])
    turn_3 = IntegerField("Turn 3", validators=[Optional(), NumberRange(min=0, max=27)])
    turn_4 = IntegerField("Turn 4", validators=[Optional(), NumberRange(min=0, max=27)])
    turn_5 = IntegerField("Turn 5", validators=[Optional(), NumberRange(min=0, max=27)])
    turn_6 = IntegerField("Turn 6", validators=[Optional(), NumberRange(min=0, max=27)])
    turn_7 = IntegerField("Turn 7", validators=[Optional(), NumberRange(min=0, max=27)])
    turn_8 = IntegerField("Turn 8", validators=[Optional(), NumberRange(min=0, max=27)])
    turn_9 = IntegerField("Turn 9", validators=[Optional(), NumberRange(min=0, max=27)])
    turn_10 = IntegerField(
        "Turn 10", validators=[Optional(), NumberRange(min=0, max=27)]
    )
    submit = SubmitField("Save All Scores")
