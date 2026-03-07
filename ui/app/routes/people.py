from flask import Flask, render_template, request, Blueprint
import db
import json
from .. import utilities as utl

people_bp = Blueprint('people', __name__)


@people_bp.route('/')
def get_people():
    data = db.people.get_people()

    return render_template('people.html', data=data)

@people_bp.route('/<int:p_id>')
def get_person(p_id):
    person = db.people.get_person(p_id)
    adjudications = db.people.get_adjudication_records(p_id)
    entries = db.people.get_entry_records(p_id)
    
    alignment_data = {
        'score': f'{round(float(person["score"])*100, 2)}%',
        'status': utl.get_score_status(person['score']),
        'comment': utl.get_score_comment(person['score']),
    }

    return render_template('person_profile.html', person_data=person, adjudications=adjudications, entries=entries, alignment_data=alignment_data)

@people_bp.route("/leaderboard")
def get_leaderboard():
    data = db.people.get_adjudicators_leaderboard()

    for person in data:
        person["alignment_data"] = {
        'score': f'{round(float(person["score"])*100, 2)}%',
        'status': utl.get_score_status(person['score']),
        'comment': utl.get_score_comment(person['score']),
    }

    print(data)
    return render_template("leaderboard.html", data=data)

@people_bp.route('/add', methods=["POST"])
def add_person():
    
    db.people.create_person(request.form.get("name"))

    return ""

@people_bp.route('/edit/<int:id>', methods=["PUT"])
def edit_person(id):
    
    db.people.update_person(id, request.form.get("name"))

    return ""

@people_bp.route('/edit/<int:id>', methods=["PUT"])
def del_person(id):
    
    for judge in db.adjudicators.get_adjudicators_by_person(id):
        db.adjudicators.delete_adjudicator(judge['id'])
    for comp in db.entries.get_entries_by_person(id):
        db.entries.delete_entry(comp['id'])
    db.people.del_person(id)

    return ""

