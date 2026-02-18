import parser.flymark as psr
import analytics.main as anl
import pandas as pd
from io import StringIO
import time

def parse_data(file):
    temp_path = f"/tmp/{file.filename}"
    file.save(temp_path)
    
    marks = psr.get_final_marks(temp_path)
    competitors = psr.get_competitors(temp_path)
    adjudicators = psr.get_adjudicators(temp_path)

    return marks, competitors, adjudicators

def get_accuracy_table_data(marks, adjudicators):
    accuracy = anl.get_overall_panel_final_accuracy(marks) 
    accuracy.index.name = 'letter'

    df = accuracy.reset_index().round(2)
    name_map = {adj['letter']: adj['name'] for adj in adjudicators}
    records = df.to_dict(orient='records')

    def get_status(score):
        if score is None: 
            return 'ghost'
        if score >= 0.8: return 'status-excellent'    
        elif score >= 0.7: return 'status-good'        
        elif score >= 0.6: return 'status-average'      
        
        elif score >= 0.4: return 'status-below-average'
        elif score >= 0.1: return 'status-poor'
        
        elif score >= -0.2: return 'status-bad'
        elif score >= -0.5: return 'status-terrible'
        else: return 'status-critical'

    final_data = []
    for row in records:
        processed_row = {
            'letter': row['letter'],
            'name': name_map.get(row['letter'], row['letter']),
            'overall': {
                'val': row.get('overall_accuracy'),
                'status': get_status(row.get('overall_accuracy'))
            },
            'dances': {}
        }
        
        for key, value in row.items():
            if key not in ['letter', 'overall_accuracy']:
                processed_row['dances'][key] = {
                    'val': value,
                    'status': get_status(value)
                }
        
        final_data.append(processed_row)

    return final_data

from collections import defaultdict

def get_bias_data(marks, adjudicators, competitors, threshold=2):
    bias_df = anl.get_overall_panel_final_bias(marks)
    
    comp_map = {str(c['number']): c['dancers'] for c in competitors}
    adj_map = {a['letter']: a['name'] for a in adjudicators}

    system_cols = ['judge', 'couple', 'overall_bias']
    dance_cols = [col for col in bias_df.columns if col not in system_cols]
    
    # Use a dictionary to group reports by judge
    grouped_reports = defaultdict(list)

    for _, row in bias_df.iterrows():
        val = row['overall_bias']
        couple_num = str(int(row['couple']))
        judge_letter = row['judge']
        
        if abs(val) < threshold:
            status = "neutral"
        else:
            status = "favoritism" if val > 0 else "opposition"
        
        dances = []
        for d in dance_cols:
            d_val = int(row[d])
            prefix = "+" if d_val > 0 else ""
            dances.append(f"{d}: {prefix}{d_val}")
        
        dancers = comp_map.get(couple_num, [{'name': 'Unknown'}, {'name': 'Unknown'}])
        
        judge_display = f"{judge_letter} {adj_map.get(judge_letter, 'Unknown')}"
        
        # Append to the existing array for this judge
        grouped_reports[judge_display].append({
            "overall": f"{'+' if val > 0 else ''}{val}",
            "name1": dancers[0]['name'],
            "name2": dancers[1]['name'] if len(dancers) > 1 else "",
            "number": couple_num,
            "type": status,
            "details": " / ".join(dances)
        })

    # Return as a standard dict for Jinja
    return dict(grouped_reports)


def get_voting_blocs(marks, adjudicators):
    coalition_report = anl.get_coalition_report(marks)
    blocs = anl.find_voting_blocs(coalition_report)

    adj_map = {a['letter']: a['name'] for a in adjudicators}

    data = [
        {
            "judges": [
                {"letter": adj, "name": adj_map.get(adj, "Unknown")}
                for adj in bloc
            ]
        }
        for bloc in blocs
    
    ]
    
    return data