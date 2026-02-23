from flask import Blueprint, render_template

events_bp = Blueprint('events', __name__)

@events_bp.route('/login')
def login():
    return render_template('login.html')