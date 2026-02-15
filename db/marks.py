import json
import io
import pandas as pd
from .utilities import execute_write, execute_read_one, execute_read_all

def save_marks(round_id, marks_json):
    existing = execute_read_one("SELECT id FROM marks WHERE round_id = ?", (round_id,))
    if existing:
        return execute_write("UPDATE marks SET marks = ? WHERE round_id = ?", (marks_json, round_id))
    else:
        return execute_write("INSERT INTO marks (round_id, marks) VALUES (?, ?)", (round_id, marks_json))

def get_marks(round_id):
    row = execute_read_one("SELECT * FROM marks WHERE round_id = ?", (round_id,))
    
    if row:
        raw_json = json.loads(row['marks'])
        parsed_marks = {
            dance: pd.read_json(io.StringIO(df_json), orient='split') 
            for dance, df_json in raw_json.items()
        }
        return parsed_marks

    return None

def delete_marks(round_id):
    return execute_write("DELETE FROM marks WHERE round_id = ?", (round_id,))