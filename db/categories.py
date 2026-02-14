from db.utilities import execute_write, execute_read_one, execute_read_all

def create_category(competition_id, name, metadata=None):
    return execute_write("INSERT INTO categories (competition_id, name, metadata) VALUES (?, ?, ?)", 
                         (competition_id, name, metadata))

def get_category(category_id):
    return execute_read_one("SELECT * FROM categories WHERE id = ?", (category_id,))

def get_category_by_comp_and_name(competition_id, name):
    return execute_read_one("SELECT * FROM categories WHERE competition_id = ? AND name = ?", 
                            (competition_id, name))

def list_categories(competition_id):
    return execute_read_all("SELECT * FROM categories WHERE competition_id = ? ORDER BY name", 
                            (competition_id,))

def update_category(category_id, name, metadata=None):
    return execute_write("UPDATE categories SET name = ?, metadata = ? WHERE id = ?", 
                         (name, metadata, category_id))

def delete_category(category_id):
    return execute_write("DELETE FROM categories WHERE id = ?", (category_id,))