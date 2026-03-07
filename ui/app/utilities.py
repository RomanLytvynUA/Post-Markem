import parser.flymark as psr
import analytics.main as anl
import db
import pandas as pd
from io import StringIO
import time
import json
from collections import defaultdict

EXCLUDE_ADJUDICATOR_MD = {'name', 'letter'}
EXCLUDE_COMPETITOR_MD = {'name', 'number', 'dancers', 'place'}

def serialize_metadata(data, exclude_keys):
    clean_dict = {
        k: v for k, v in data.items() 
        if k not in exclude_keys
    }

    return json.dumps(clean_dict, ensure_ascii=False)


def translate_dance(dance):
    dances = {
        'C': 'Cha-cha-cha',
        'S': 'Samba',
        'R': 'Rumba',
        'P': 'Paso Doble',
        'J': 'Jive',

        'W': 'Slow Waltz',
        'T': 'Tango',
        'V': 'Viennese Waltz',
        'F': 'Slow Foxtrot',
        'Q': 'Quickstep'
    }

    return dances.get(dance, dance)


def clear_adjudicators(round_id):
    for adj in db.adjudicators.get_adjudicators_by_round(round_id):
        db.adjudicators.delete_adjudicator(adj['id'])


def add_adjudicators(adj_list, round_id):
    for adj in adj_list:
        meta_json = serialize_metadata(adj, EXCLUDE_ADJUDICATOR_MD)
        person_id = db.create_person(adj['name'], metadata=meta_json)
        db.create_adjudicator(round_id, person_id, adj['letter'], metadata=meta_json)


def clear_entries(cat_id):
    for entry in db.entries.list_entries(cat_id):
        db.entries.delete_entry(entry['id'])


def clear_marks(round_id):
    marks = db.marks.get_raw_marks(round_id)
    db.analytics.delete_analytics_cache(marks['id'])
    db.analytics.del_alignment_score(marks['id'])
    if marks: db.marks.delete_marks(marks['id'])


def add_entries(entries_list, cat_id):
    for comp in entries_list:
        entry_meta = serialize_metadata(comp, EXCLUDE_COMPETITOR_MD)

        p1_data = comp["dancers"][0]
        p1_id = db.create_person(p1_data["name"], metadata=serialize_metadata(p1_data, {'name'}))
        
        p2_id = None
        if len(comp["dancers"]) > 1:
            p2_data = comp["dancers"][1]
            p2_id = db.create_person(p2_data["name"], metadata=serialize_metadata(p2_data, {'name'}))
        
        db.create_entry(cat_id, comp["number"], comp['place'], p1_id, p2_id, metadata=entry_meta)


def parse_data(file, marks_as_json=False):
    temp_path = f"/tmp/{file.filename}"
    file.save(temp_path)
    
    marks = psr.get_final_marks(temp_path, as_json=marks_as_json)

    competitors = psr.get_competitors(temp_path)
    adjudicators = psr.get_adjudicators(temp_path)

    return marks, competitors, adjudicators


def save_alignment_score(marks_id, person_id, score):
    return


def get_analytics_data(marks, cached_marks_id=None, cache=True):
    # Try cache
    data = db.analytics.get_analytics_cache(cached_marks_id) if cached_marks_id else None

    # Fallback to computing fresh data
    if not (data and all(v is not None for v in data)):
        data = [
            get_alignment_data(marks), 
            get_bias_data(marks), 
            get_voting_blocs_data(marks)
        ]
        # Cache data if requested
        if cached_marks_id and cache:
            db.analytics.save_analytics_cache(cached_marks_id, data[0], data[1], data[2])
            
    return data

def format_analysis_display_data(raw_data, competitors, adjudicators):
    alignment, bias, voting_blocs = raw_data
    
    return (
        get_alignment_display_data(alignment, adjudicators),
        get_bias_display_data(bias, adjudicators, competitors),
        get_voting_blocs_display_data(voting_blocs, adjudicators)
    )

def get_alignment_data(marks):
    return anl.get_overall_panel_final_accuracy(marks)

def get_score_status(score):
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

def get_score_comment(score):
    if score is None: 
        return ''
    if score >= 0.8: return 'Excellent reputation, amazing regular panel alignment'    
    elif score >= 0.7: return 'Decent reputation, high regular panel alignment'        
    elif score >= 0.6: return 'Average reputation, moderate panel alignment'      
    elif score >= 0.4: return 'Below average reputation, inconsistent panel alignment'
    elif score >= 0.1: return 'Poor reputation, highly irregular panel alignment'
    elif score >= -0.2: return 'Terrible reputation, random marking patterns'
    elif score >= -0.5: return 'Critical reputation, marks actively opposite to the panel'
    else: return 'Severe variance, inverted panel alignment'

def get_alignment_display_data(alignment_data, adjudicators):
    alignment_data.index.name = 'letter'

    df = alignment_data.reset_index().round(2)
    name_map = {adj['letter']: adj['name'] for adj in adjudicators}
    records = df.to_dict(orient='records')


    final_data = []
    for row in records:
        processed_row = {
            'letter': row['letter'],
            'name': name_map.get(row['letter'], row['letter']),
            'overall': {
                'val': row.get('overall_accuracy'),
                'status': get_score_status(row.get('overall_accuracy'))
            },
            'dances': {}
        }
        
        for key, value in row.items():
            if key not in ['letter', 'overall_accuracy']:
                processed_row['dances'][key] = {
                    'val': value,
                    'status': get_score_status(value)
                }
        
        final_data.append(processed_row)

    return final_data


def get_competitors_map(competitors):
    """Normalize the parser's output to the competitors map"""
    data = competitors
    for comp in data:
        comp['p1_name'] = comp['dancers'][0]['name']if len(comp['dancers']) > 0 else 'Unknown dancer'
        comp['p2_name'] = comp['dancers'][1]['name'] if len(comp['dancers']) > 1 else ""
    return data
                

def get_bias_data(marks):
    return anl.get_overall_panel_final_bias(marks)


def get_bias_display_data(bias_data, adjudicators, competitors, threshold=2):
    comp_map = {str(c['number']): c for c in competitors}
    adj_map = {a['letter']: a['name'] for a in adjudicators}

    system_cols = ['judge', 'couple', 'overall_bias']
    dance_cols = [col for col in bias_data.columns if col not in system_cols]
    
    # group reports by judge
    grouped_reports = defaultdict(list)

    for _, row in bias_data.iterrows():
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
        
        grouped_reports[judge_display].append({
            "overall": f"{'+' if val > 0 else ''}{val}",
            "name1": dancers['p1_name'],
            "name2": dancers['p2_name'],
            "number": couple_num,
            "type": status,
            "details": " / ".join(dances)
        })

    return dict(grouped_reports)


def get_voting_blocs_data(marks):
    return anl.find_voting_blocs(anl.get_coalition_report(marks))


def get_voting_blocs_display_data(blocs_data, adjudicators):
    adj_map = {a['letter']: a['name'] for a in adjudicators}

    data = [
        {
            "name": f"Bloc #{i+1}",
            "judges": [
                {"letter": adj, "name": adj_map.get(adj, "Unknown")}
                for adj in bloc
            ]
        }
        for i, bloc in enumerate(blocs_data)
    
    ]
    
    return data

def save_alignment_scores(alignment_report, adjudicators, marks_id):
    adj_map = {a['letter']: a['person_id'] for a in adjudicators}

    for index, row in alignment_report.iterrows():
        db.save_alignment_score(marks_id, adj_map[index], row['overall_accuracy'])

def delete_round_data(round_id):
    judges = db.adjudicators.get_adjudicators_by_round(round_id)
    for judge in judges:
        db.adjudicators.delete_adjudicator(judge['id'])
    
    raw_marks = db.marks.get_raw_marks(round_id)
    if raw_marks:
        db.analytics.delete_analytics_cache(raw_marks['id'])
        db.analytics.del_alignment_score(raw_marks['id'])
    
    db.marks.delete_marks(round_id)
    db.rounds.delete_round(round_id)

def delete_category_data(category_id):
    entries = db.entries.list_entries(category_id)
    for entry in entries:
        db.entries.delete_entry(entry['id'])
    
    rounds = db.rounds.list_rounds(category_id)
    for round_item in rounds:
        delete_round_data(round_item['id'])
    
    db.categories.delete_category(category_id)

def delete_competition(comp_id):
    categories = db.categories.list_categories(comp_id)
    for category in categories:
        delete_category_data(category['id'])
    
    db.competitions.delete_competition(comp_id)
