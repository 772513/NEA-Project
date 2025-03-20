from flask import render_template
from flask import Blueprint
from app.forms import LoginForm

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    user = {'username':'Ivansia'}
    matches = [
        {
            'opponent':'death knights',
            'date':'25-03-25 18:00',
            'location':'Gloucester'
        }
    ]
    return render_template('index.html', title='Home', user=user, matches=matches)


@main.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)