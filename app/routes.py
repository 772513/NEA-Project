from datetime import datetime, timezone
from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import (
    LoginForm,
    RegistrationForm,
    EditProfileForm,
    AddMatchForm,
    AddScoreForm,
)
from app.models import User, Score, Match


@app.route("/")
@app.route("/index")
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


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(url_for("index"))
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
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
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/user/<username>")
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    matches = [
        {"opponent": "opponent1", "location": "location1", "author": user},
        {"opponent": "opponent2", "location": "location2", "author": user},
    ]
    return render_template("user.html", user=user, matches=matches)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
    return render_template("edit_profile.html", title="Edit Profile", form=form)


@app.route("/matches", methods=["GET", "POST"])
@login_required
def matches():
    form = AddMatchForm()
    if form.validate_on_submit():
        try:
            match_date = datetime.strptime(form.date.data, "%Y-%m-%d")
        except ValueError:
            match_date = None
        match = Match(
            opponent=form.opponent.data,
            location=form.location.data,
            timestamp=match_date,
        )
        db.session.add(match)
        db.session.commit()

    matches = Match.query.all()
    return render_template("matches.html", title="Matches", matches=matches, form=form)


@app.route("/match/<int:id>", methods=["GET", "POST"])
def match(id):
    match = Match.query.get_or_404(id)
    form = AddScoreForm()
    if form.validate_on_submit():
        turn_numbers = (
            db.session.query(Score.turn_number)
            .filter(Score.match_id == match.id, Score.user_id == current_user.id)
            .order_by(Score.turn_number.desc())
            .all()
        )
        if turn_numbers:
            turn_number = turn_numbers[0][0] + 1
        else:
            turn_number = 1

        score = Score(
            user_id=current_user.id,
            match_id=match.id,
            turn_number=turn_number,
            score=form.score.data,
        )

        db.session.add(score)
        db.session.commit()

    usernames = (
        db.session.gquery(User.username)
        .join(Score.user_id == User.id)
        .filter(Score.match_id == match.id)
        .all()
    )
    scores = Score.query.filter_by(match_id=match.id).all()
    return render_template(
        "match.html", id=id, usernames=usernames, scores=scores, form=form
    )
