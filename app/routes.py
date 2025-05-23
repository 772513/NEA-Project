from datetime import datetime, timezone
from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
import sqlalchemy as sa
import sqlalchemy.orm
from sqlalchemy.orm import joinedload
from app import app, db
from app.forms import (
    LoginForm,
    RegistrationForm,
    UpdateProfileForm,
    ChangePasswordForm,
    CRMatchForm,
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
        if not user.is_active:
            flash("This account has been deactivated.", "danger")
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
    user = (
        db.session.execute(sa.select(User).where(User.username == username))
        .scalars()
        .first()
    )

    if current_user == user:
        profile_form = UpdateProfileForm(obj=current_user)
        password_form = ChangePasswordForm()
    else:
        profile_form = None
        password_form = None

    if (
        profile_form
        and profile_form.validate_on_submit()
        and "update_profile" in request.form
    ):
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("user", username=current_user.username))

    if (
        password_form
        and password_form.validate_on_submit()
        and "change_password" in request.form
    ):
        if not check_password_hash(
            current_user.password, password_form.current_password.data
        ):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.password = generate_password_hash(
                password_form.new_password.data
            )
            db.session.commit()
            flash("Password changed successfully!", "success")
            return redirect(url_for("user"))

    matches = (
        db.session.execute(
            sa.select(Match)
            .join(Score)
            .where(Score.user_id == user.id)
            .order_by(Match.timestamp.desc())
            .distinct()
        )
        .scalars()
        .all()
    )
    return render_template(
        "user.html",
        user=user,
        matches=matches,
        profile_form=profile_form,
        password_form=password_form,
    )


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    profile_form = UpdateProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    if profile_form.validate_on_submit() and "update_profile" in request.form:
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    if password_form.validate_on_submit() and "change_password" in request.form:
        if not current_user.check_password(password_form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash("Password changed successfully!", "success")
            return redirect(url_for("profile"))

    return render_template(
        "profile.html",
        profile_form=profile_form,
        password_form=password_form,
    )


@app.route("/user/delete/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if user_id != current_user.id:
        flash("you are not authorised to delete this account.", "datnger")
        return redirect(url_for("user", username=current_user.username))

    user = current_user

    # dactivate account
    user.is_active = False
    db.session.commit()

    flash("Your account has been deleted.", "success")
    return redirect(url_for("matches"))


@app.route("/")
@app.route("/index")
@app.route("/matches")
@login_required
def matches():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    all_matches = Match.query.order_by(Match.timestamp.desc()).all()
    return render_template(
        "matches.html", matches=all_matches, title="Matches", timestamp=timestamp
    )


@app.route("/matches/delete/<int:match_id>", methods=["POST"])
@login_required
def delete_match(match_id):
    try:
        print(f"Deleting match iwth ID: {match_id}")
        match = Match.query.get_or_404(match_id)

        print(f"Found match: {match.id}")

        # if match.match_scores:
        #     if isinstance(match.match_scores, list):
        for score in match.match_scores:
            db.session.delete(score)
            print(f"Deleted score with ID: {score.id}")
            # else:
            #     db.session.delete(match.match_scores)
            #     print(f"Deleted score with ID: {match.match_score.id}")

        db.session.delete(match)
        print(f"Deleted match with ID: {match.id}")

        db.session.commit()
        print("Commit successful")

    except Exception as e:
        print(f"Error: {str(e)}")
        db.session.rollback()
        flash("An error occurred while deleting the match. Please try again.", "error")
        return redirect(url_for("matches"))

    flash("Match deleted successfully!", "success")
    return redirect(url_for("matches"))


@app.route("/match", methods=["GET", "POST"])
@app.route("/match/edit/<int:match_id>", methods=["GET", "POST"])
@login_required
def match_form(match_id=None):
    match = Match.query.get(match_id) if match_id else None
    form = CRMatchForm(obj=match)

    if form.validate_on_submit():
        try:
            date = datetime.strptime(form.date.data, "%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            flash("Invalid date format. Please use YYYY-MM-DD HH:MM", "danger")
            return render_template("edit_match.html", form=form, match=match)

        if match:
            # editing existing match
            match.opponent = form.opponent.data
            match.location = form.location.data
            match.timestamp = date
            flash("Match updated!", "success")
        else:
            # creating new match
            match = Match(
                opponent=form.opponent.data,
                location=form.location.data,
                timestamp=date,
            )
            db.session.add(match)
            flash("New match created!", "success")

        db.session.commit()
        return redirect(url_for("matches"))

    if request.method == "GET" and match:
        form.opponent.data = match.opponent
        form.location.data = match.location
        form.date.data = (
            match.timestamp.strftime("%Y-%m-%d %H:%M") if match.timestamp else ""
        )

    return render_template("edit_match.html", form=form, match=match)


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
        turn_numbers = [
            scores[username][i].turn_number for i in range(0, len(scores[username]))
        ]
        temp_scores = [
            scores[username][i].score for i in range(0, len(scores[username]))
        ]

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
