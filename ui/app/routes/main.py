from flask import Blueprint, render_template, request
from .. import utilities as utl
import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@main_bp.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['file']
    
    marks, competitors, adjudicators = utl.parse_data(file)
    analytics_data = utl.get_analytics_data(marks)
    accuracy_table_data, bias_data, voting_blocs = utl.format_analysis_display_data(analytics_data, utl.get_competitors_map(competitors), adjudicators)

    return render_template(
        'partials/report.html',
        competitors=competitors,
        adjudicators=adjudicators,
        accuracy_table_data=accuracy_table_data,
        bias_data=bias_data,
        voting_blocs=voting_blocs)

@main_bp.route('/analyse_round/<int:round_id>', methods=['POST'])
def analyze_round(round_id):
    marks, marks_id = db.marks.get_marks(round_id)
    adjudicators = db.adjudicators.get_adjudicators_by_round(round_id)
    competitors = db.entries.get_round_entries(round_id)

    analytics_data = utl.get_analytics_data(marks, cached_marks_id=marks_id)

    accuracy_table_data, bias_data, voting_blocs = utl.format_analysis_display_data(analytics_data, competitors, adjudicators)

    utl.save_alignment_scores(analytics_data[0], adjudicators, marks_id)

    return render_template(
        'partials/report.html',
        competitors=competitors,
        adjudicators=adjudicators,
        accuracy_table_data=accuracy_table_data,
        bias_data=bias_data,
        voting_blocs=voting_blocs,
        include_header=False)
