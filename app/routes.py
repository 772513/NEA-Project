from flask import render_template, flash, redirect, url_for
from flask import Blueprint
from app.forms import LoginForm

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/index")
def index():
    user = {"username": "Ivansia"}
    matches = [
        {
            "opponent": "death knights",
            "date": "25-03-25 18:00",
            "location": "Gloucester",
        }
    ]
    return render_template("index.html", title="Home", user=user, matches=matches)


@main.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(
            "Login requested for user {}, remember_me={}".format(
                form.username.data, form.remember_me.data
            )
        )
        return redirect(url_for('main.index'))
    return render_template("login.html", title="Sign In", form=form)
