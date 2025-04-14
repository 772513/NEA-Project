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
    Length,
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
    username = StringField("Username", validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    forename = StringField("Forename", validators=[DataRequired()])
    surname = StringField("Surname", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    password_check = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError("Please use a different username.")


class UpdateProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Update Profile")

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField("Confirm New Password", validators=[
        DataRequired(),
        EqualTo("new_password", message="Passwords must match.")
    ])
    submit = SubmitField("Change Password")


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
