import json
import io
import pandas as pd
from .utilities import execute_write, execute_read_one, execute_read_all

def save_analytics_cache(marks_id, accuracy_df, bias_df, voting_blocs):
    """
    Serializes the three DataFrames and the blocs list, then upserts them.
    """
    existing = execute_read_one("SELECT marks_id FROM analytics_cache WHERE marks_id = ?", (marks_id,))
    
    align_json = accuracy_df.to_json(orient='split') if not accuracy_df.empty else None
    bias_json = bias_df.to_json(orient='split') if not bias_df.empty else None
    blocs_json = json.dumps(voting_blocs)
    
    if existing:
        query = """
            UPDATE analytics_cache 
            SET alignment_cache = ?, bias_cache = ?, blocs_cache = ?, last_calculated = CURRENT_TIMESTAMP
            WHERE marks_id = ?
        """
        return execute_write(query, (align_json, bias_json, blocs_json, marks_id))
    else:
        query = """
            INSERT INTO analytics_cache (marks_id, alignment_cache, bias_cache, blocs_cache) 
            VALUES (?, ?, ?, ?)
        """
        return execute_write(query, (marks_id, align_json, bias_json, blocs_json))


def get_analytics_cache(marks_id):
    """
    Thaws the JSON strings back into live Pandas DataFrames.
    Returns the exact same tuple format as the analytics engine:
    (accuracy_df, bias_df, voting_blocs)
    """
    row = execute_read_one("SELECT * FROM analytics_cache WHERE marks_id = ?", (marks_id,))
    
    if row:
        def parse_df(json_str):
            if not json_str:
                return pd.DataFrame()
            return pd.read_json(io.StringIO(json_str), orient='split')

        accuracy_df = parse_df(row["alignment_cache"])
        bias_df = parse_df(row["bias_cache"])
        voting_blocs = json.loads(row["blocs_cache"])

        # Returns the exact format expected by your frontend logic
        return accuracy_df, bias_df, voting_blocs
        
    return None, None, None


def delete_analytics_cache(marks_id):
    """Flushes the cache for a specific marking sheet."""
    return execute_write("DELETE FROM analytics_cache WHERE marks_id = ?", (marks_id,))

def save_alignment_score(marks_id, person_id, score):
    """Upserts an alignment score for a specific person on a specific marking sheet."""
    existing = execute_read_one(
        "SELECT id FROM alignment_records WHERE marks_id = ? AND person_id = ?", 
        (marks_id, person_id)
    )
    
    if existing:
        return execute_write(
            "UPDATE alignment_records SET alignment = ? WHERE marks_id = ? AND person_id = ?", 
            (score, marks_id, person_id)
        )
    else:
        return execute_write(
            "INSERT INTO alignment_records (alignment, person_id, marks_id) VALUES (?, ?, ?)", 
            (score, person_id, marks_id)
        )

def del_alignment_score(marks_id):
    """Deletes all alignment records associated with a specific marking sheet."""
    return execute_write("DELETE FROM alignment_records WHERE marks_id = ?", (marks_id,))
