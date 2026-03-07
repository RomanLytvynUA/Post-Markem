from flask import Flask, render_template, request, Blueprint
import db
import json
from .. import utilities as utl

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/add', methods=["POST"])
def add_category():
    category_id = db.categories.create_category(request.form.get("comp_id"), request.form.get("name"))
    rounds = request.form.getlist("rounds[]")

    rounds.reverse()
    for round in rounds:
        db.rounds.create_round(category_id, round)
    
    data = db.categories.get_category(category_id)
    data["rounds"] = db.rounds.list_rounds(category_id)
    return render_template('partials/events_components/category_row.html', category=data)

@categories_bp.route('/edit/<string:cat_id>', methods=["PUT"])
def edit_category(cat_id):
    db.categories.update_category(cat_id, request.form.get("name"))

    new_round_ids = request.form.getlist("round_ids[]")
    new_round_names = request.form.getlist("round_names[]")
    
    old_round_ids = [str(r['id']) for r in db.rounds.list_rounds(cat_id)]

    # DELETE
    for old_id in old_round_ids:
        if old_id not in new_round_ids:
            for judge in db.adjudicators.get_adjudicators_by_round(old_id):
                db.adjudicators.delete_adjudicator(judge['id'])
            db.analytics.delete_analytics_cache(db.marks.get_raw_marks(old_id)['id'])
            db.marks.delete_marks(old_id)
            db.rounds.delete_round(old_id)

    # UPDATE or CREATE
    for round_id, round_name in zip(new_round_ids, new_round_names):
        if round_id == "":
            db.rounds.create_round(cat_id, round_name)
        else:
            db.rounds.update_round(round_id, round_name)

    data = db.categories.get_category(cat_id)
    data["rounds"] = db.rounds.list_rounds(cat_id)
    
    return render_template('partials/events_components/category_row.html', category=data)

@categories_bp.route('/del/<string:cat_id>', methods=["DELETE"])
def del_category(cat_id):
    utl.delete_category_data(cat_id)
    return ""

from flask import abort

@categories_bp.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    
    round_id = request.form.get("round_id")
    cat_id = request.form.get("cat_id")
    comp_id = request.form.get("comp_id")
    extraction_type = request.form.get('extraction_type')

    match(extraction_type):
        case "fm_html":
            marks, competitors, adjudicators = utl.parse_data(file, marks_as_json=True)

            utl.clear_adjudicators(round_id)
            utl.clear_entries(cat_id)
            utl.clear_marks(round_id)
            
            utl.add_adjudicators(adjudicators, round_id)
            utl.add_entries(competitors, cat_id)
            db.marks.save_marks(round_id, marks)
        case _:
            pass
    
    # run and cache the analysis
    marks, marks_id = db.marks.get_marks(round_id)
    adjudicators = db.adjudicators.get_adjudicators_by_round(round_id)
    analytics_data = utl.get_analytics_data(marks, cached_marks_id=marks_id)
    utl.save_alignment_scores(analytics_data[0], adjudicators, marks_id)

    return "Upload complete", 200

@categories_bp.route('/display/<int:round_id>')
def display_category(round_id):
    round_data = db.rounds.get_round(round_id)
    if not round_data:
        abort(404) 

    cat_id = round_data.get('category_id')
    category = db.categories.get_category(cat_id)
    rounds = db.rounds.list_rounds(cat_id)
    competition = db.competitions.get_competition(category['competition_id'])

    competitors = db.entries.get_round_entries(round_id)
    for comp in competitors:
        p2 = f" & {comp.get('p2_name')}" if comp.get('p2_name') else ""
        comp['name'] = f"{comp.get('p1_name')}{p2}"

    def safe_place_sort(comp):
        try:
            return int(str(comp.get('place', '999')).split()[0])
        except (ValueError, AttributeError):
            return 999
            
    competitors.sort(key=safe_place_sort)
 
    adjudicators = db.adjudicators.get_adjudicators_by_round(round_id)

    raw_marks, _ = db.marks.get_marks(round_id)
    marks = {}
    if raw_marks:
        for dance, df in raw_marks.items():
            translated_dance = utl.translate_dance(dance) 
            df.index = df.index.astype(int) 
            marks[translated_dance] = df.reset_index(names='number').to_dict('records')

    data_missing = False
    if not raw_marks or len(adjudicators) < 0 or len(competitors) < 0 :
        data_missing = True

    return render_template(
        'category_overview.html', 
        selected_round=round_id, 

        adjudicators=adjudicators, 
        competitors=competitors,
        marks=marks, 

        data_missing=data_missing,

        rounds=rounds, 
        round_data=round_data, 
        category=category,
        competition=competition
    )
