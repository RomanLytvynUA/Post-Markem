from flask import Flask, render_template, request
from . import utilities as utl

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['file']
    
    marks, competitors, adjudicators = utl.parse_data(file)

    accuracy_table_data = utl.get_accuracy_table_data(marks, adjudicators)
    bias_data = utl.get_bias_data(marks, adjudicators, competitors)
    voting_blocs = utl.get_voting_blocs(marks, adjudicators)

    return render_template(
        'partials/report.html',
        competitors=competitors,
        adjudicators=adjudicators,
        accuracy_table_data=accuracy_table_data,
        bias_data=bias_data,
        voting_blocs=voting_blocs)

if __name__ == '__main__':
    app.run(debug=True, port=5050)