from datetime import datetime, timezone
from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import (
    LoginForm,
    RegistrationForm,
    EditProfileForm,
    AddMatchForm,
    EditMatchForm,
    AddScoreForm,
    EditScoresForm,
)
from app.models import User, Score, Match


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("matches"))
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
            next_page = url_for("matches")
        return redirect(url_for("matches"))
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("matches"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("matches"))
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


@app.route("/")
@app.route("/index")
@app.route("/matches", methods=["GET", "POST"])
@login_required
def matches():
    form = AddMatchForm()
    if form.validate_on_submit():
        try:
            date = datetime.strptime(form.date.data, "%Y-%m-%d %H:%M")
        except ValueError:
            date = None
        match = Match(
            opponent=form.opponent.data,
            location=form.location.data,
            timestamp=date,
        )
        db.session.add(match)
        db.session.commit()

        return redirect(url_for("matches"))

    matches = Match.query.all()
    return render_template("matches.html", title="Matches", matches=matches, form=form)


@app.route("/match/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_match(id):
    match = Match.query.get_or_404(id)
    form = EditMatchForm()

    if form.validate_on_submit():
        match.opponent = form.opponent.data
        match.location = form.location.data
        match.timestamp = datetime.strptime(form.date.data, "%Y-%m-%d %H:%M")

        try:
            db.session.commit()
            flash("Match updated succesfully!", "success")
            return redirect(url_for("matches"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating match: {str(e)}", "danger")

    form.opponent.data = match.opponent
    form.location.data = match.location
    form.date.data = match.timestamp.strftime("%Y-%m-%d %H:%M")

    return render_template(
        "edit_match.html", form=form, match=match, title=f"Edit Match {id}"
    )


@app.route("/match/<int:id>", methods=["GET", "POST"])
def match(id):
    def get_form_field(form, name):
        return getattr(form, name)

    match = Match.query.get_or_404(id)

    # preload existing scores into a dict by turn number
    existing_scores = {
        score.turn_number: score
        for score in Score.query.filter_by(
            match_id=match.id, user_id=current_user.id
        ).all()
    }

    form = EditScoresForm()

    if form.validate_on_submit():
        for turn in range(1, 11):
            field = getattr(form, f"turn_{turn}")
            score_value = field.data

            if score_value is not None:
                if turn in existing_scores:
                    # update existing score
                    existing_scores[turn].score = score_value
                else:
                    # add new score
                    new_score = Score(
                        user_id=current_user.id,
                        match_id=match.id,
                        turn_number=turn,
                        score=score_value,
                    )
                    db.session.add(new_score)

        db.session.commit()
        return redirect(url_for("match", id=match.id))

    # prepopulate the form with existing scores
    for turn, score_obj in existing_scores.items():
        getattr(form, f"turn_{turn}").data = score_obj.score

    # get list of usernames and scores for the match
    usernames = {
        username[0]: User.query.filter_by(username=username[0]).first().id
        for username in db.session.query(User.username)
        .join(Score, Score.user_id == User.id)
        .filter(Score.match_id == match.id)
        .all()
    }

    scores = {
        username: [
            score
            for score in Score.query.filter_by(
                match_id=match.id, user_id=usernames.get(username)
            )
            .order_by(Score.turn_number.asc())
            .all()
        ]
        for username in usernames
    }

    turns = {}
    for username in scores:
        turns[username] = []
        turn_numbers = [scores[username][i].turn_number for i in range(0, len(scores[username]))]
        temp_scores = [scores[username][i].score for i in range(0, len(scores[username]))]

        offset = 1
        for turn in range(1, 11):
            print(turn, turn - offset, turn_numbers[turn - offset])
            if turn == turn_numbers[turn - offset]:
                turns[username].append(temp_scores[turn - offset])
                print(f"score: {temp_scores[turn - offset]}")
            else:
                turns[username].append("None")
                offset += 1
    print(turns)

    # render the page with the forms and scores
    return render_template(
        "match.html",
        id=id,
        form=form,
        turns=turns,
        scores=scores,
        usernames=usernames,
        get_form_field=get_form_field,
    )


@app.route("/remove_score/<int:match_id>", methods=["POST"])
@login_required
def remove_score(match_id):
    # get match and ensure validity
    match = Match.query.get_or_404(match_id)

    selected_turn = request.form.get("turn_to_remove")

    if selected_turn:
        turn_number = int(selected_turn)

        score = Score.query.filter_by(
            match_id=match.id, user_id=current_user.id, turn_number=turn_number
        ).first()

        if score:
            db.session.delete(score)
            db.session.commit()

    return redirect(url_for("match", id=match.id))
