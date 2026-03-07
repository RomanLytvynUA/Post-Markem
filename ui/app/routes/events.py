from flask import Flask, render_template, request, Blueprint
import db
from .. import utilities as utl

events_bp = Blueprint('events_bp', __name__)

@events_bp.route('/')
def get_events():
    return render_template('events.html', competitions=db.list_competitions())

@events_bp.route('/add', methods=["POST"])
def add_event():
    comp_id = db.competitions.create_competition(request.form.get("name"), request.form.get("date"))
    
    return render_template('partials/events_components/event_card.html', comp=db.competitions.get_competition(comp_id))

@events_bp.route('/edit/<string:comp_id>', methods=["PUT"])
def edit_event(comp_id):
    db.competitions.update_competition(comp_id, request.form.get("name"), request.form.get("date"))
    
    return render_template('partials/events_components/event_card.html', comp=db.competitions.get_competition(comp_id))

@events_bp.route('/del/<string:comp_id>', methods=["DELETE"])
def del_event(comp_id):
    utl.delete_competition(comp_id)
    return ""

@events_bp.route('/get/<string:comp_id>')
def get_event_details(comp_id):
    categories = db.list_categories(comp_id)
    return render_template("partials/events_components/comp_details.html", comp_id=comp_id, data=[
        {**category, "rounds": db.list_rounds(category["id"])} 
        for category in categories
    ])