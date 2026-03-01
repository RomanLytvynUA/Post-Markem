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

    accuracy_table_data = utl.get_accuracy_table_data(marks, adjudicators)
    bias_data = utl.get_bias_data(marks, adjudicators, utl.get_competitors_map(competitors))
    voting_blocs = utl.get_voting_blocs(marks, adjudicators)

    return render_template(
        'partials/report.html',
        competitors=competitors,
        adjudicators=adjudicators,
        accuracy_table_data=accuracy_table_data,
        bias_data=bias_data,
        voting_blocs=voting_blocs)

@main_bp.route('/analyse_round/<int:round_id>', methods=['POST'])
def analyze_round(round_id):
    marks = db.marks.get_marks(round_id)
    adjudicators = db.adjudicators.get_adjudicators_by_round(round_id)
    competitors = db.entries.get_round_entries(round_id)

    accuracy_table_data = utl.get_accuracy_table_data(marks, adjudicators)
    bias_data = utl.get_bias_data(marks, adjudicators, competitors)
    voting_blocs = utl.get_voting_blocs(marks, adjudicators)

    return render_template(
        'partials/report.html',
        competitors=competitors,
        adjudicators=adjudicators,
        accuracy_table_data=accuracy_table_data,
        bias_data=bias_data,
        voting_blocs=voting_blocs,
        include_header=False)
