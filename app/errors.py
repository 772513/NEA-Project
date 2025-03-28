from flask import render_template, Blueprint
from app import db

main = Blueprint("main", __name__)

@main.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@main.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template('500.html'), 500