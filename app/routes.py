from flask import render_template, flash, redirect, url_for, request
from flask import Blueprint
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User
from app.forms import RegistrationForm
from urllib.parse import urlsplit

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/index")
@login_required
def index():
    matches = [
        {
            "opponent": "death knights",
            "date": "25-03-25 18:00",
            "location": "Gloucester",
        }
    ]
    return render_template("index.html", title="Home", matches=matches)


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("main.login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(url_for("main.index"))
    return render_template("login.html", title="Sign In", form=form)


@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            forename=form.forename.data,
            surname=form.surname.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("main.login"))
    return render_template("register.html", title="Register", form=form)


@main.route("/user/<username>")
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    matches = [
        {"opponent": "opponent1", "location": "location1", "author": user},
        {"opponent": "opponent2", "location": "location2", "author": user},
    ]
    return render_template("user.html", user=user, matches=matches)
