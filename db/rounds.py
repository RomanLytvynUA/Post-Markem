from .utilities import execute_write, execute_read_one, execute_read_all

def create_round(category_id, round_type, metadata=None):
    return execute_write("INSERT INTO rounds (category_id, type, metadata) VALUES (?, ?, ?)", 
                         (category_id, round_type, metadata))

def get_round(round_id):
    return execute_read_one("SELECT * FROM rounds WHERE id = ?", 
                            (round_id,))

def get_round_by_category_and_type(category_id, round_type):
    return execute_read_one("SELECT * FROM rounds WHERE category_id = ? AND type = ?", 
                            (category_id, round_type))

def list_rounds(category_id):
    return execute_read_all("SELECT * FROM rounds WHERE category_id = ?", 
                            (category_id,))

def update_round(round_id, round_type, metadata=None):
    return execute_write("UPDATE rounds SET type = ?, metadata = ? WHERE id = ?", 
                         (round_type, metadata, round_id))

def delete_round(round_id):
    return execute_write("DELETE FROM rounds WHERE id = ?", 
                         (round_id,))