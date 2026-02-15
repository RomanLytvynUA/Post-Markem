from .utilities import execute_write, execute_read_one, execute_read_all

def create_adjudicator(round_id, person_id, letter, metadata=None):
    return execute_write("INSERT INTO adjudicators (round_id, people_id, letter, metadata) VALUES (?, ?, ?, ?)", 
                         (round_id, person_id, letter, metadata))

def get_adjudicator(adjudicator_id):
    return execute_read_one("SELECT * FROM adjudicators WHERE id = ?", (adjudicator_id,))

def get_adjudicators_by_round(round_id):
    return execute_read_all("SELECT * FROM adjudicators WHERE round_id = ? ORDER BY letter", (round_id,))

def update_adjudicator(adjudicator_id, letter, metadata=None):
    # Update letter or metadata for a judge
    return execute_write("UPDATE adjudicators SET letter = ?, metadata = ? WHERE id = ?",
                         (letter, metadata, adjudicator_id))

def delete_adjudicator(adjudicator_id):
    # Remove adjudicator assignment
    return execute_write("DELETE FROM adjudicators WHERE id = ?", (adjudicator_id,))

def get_round_judges_map(round_id):
    # Get dictionary mapping letters to person names
    rows = execute_read_all("""
        SELECT a.letter, p.name 
        FROM adjudicators a
        JOIN people p ON a.people_id = p.id
        WHERE a.round_id = ?
        ORDER BY a.letter
    """, (round_id,))
    return {row['letter']: row['name'] for row in rows}