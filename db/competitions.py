from .utilities import execute_write, execute_read_one, execute_read_all

def create_competition(name, date=None, metadata=None):
    return execute_write("INSERT INTO competitions (name, date, metadata) VALUES (?, ?, ?)", (name, date, metadata))

def get_competition(competition_id):
    return execute_read_one("SELECT * FROM competitions WHERE id = ?", (competition_id,))

def get_competition_by_name(name):
    return execute_read_one("SELECT * FROM competitions WHERE name = ?", (name,))

def list_competitions():
    return execute_read_all("SELECT * FROM competitions ORDER BY date DESC, name")

def update_competition(competition_id, name, date, metadata=None):
    return execute_write("UPDATE competitions SET name = ?, date = ?, metadata = ? WHERE id = ?", 
                         (name, date, metadata, competition_id))

def delete_competition(competition_id):
    return execute_write("DELETE FROM competitions WHERE id = ?", (competition_id,))