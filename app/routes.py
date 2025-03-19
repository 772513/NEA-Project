from flask import render_template
from flask import Blueprint

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