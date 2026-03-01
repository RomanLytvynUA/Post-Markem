from flask import Flask, render_template, request, Blueprint
import db

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
    for category in db.categories.list_categories(comp_id):
        for entry in db.entries.list_entries(category["id"]):
            db.entries.delete_entry(entry['id'])
        for round in db.rounds.list_rounds(category["id"]):
            for judge in db.adjudicators.get_adjudicators_by_round(round["id"]):
                db.adjudicators.delete_adjudicator(judge['id'])
            db.marks.delete_marks(round["id"])
            db.rounds.delete_round(round['id'])
        db.categories.delete_category(category['id'])
    db.competitions.delete_competition(comp_id)

    return ""

@events_bp.route('/get/<string:comp_id>')
def get_event_details(comp_id):
    categories = db.list_categories(comp_id)
    return render_template("partials/events_components/comp_details.html", comp_id=comp_id, data=[
        {**category, "rounds": db.list_rounds(category["id"])} 
        for category in categories
    ])