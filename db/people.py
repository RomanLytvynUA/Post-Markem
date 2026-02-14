from db.utilities import execute_write, execute_read_one, execute_read_all

def create_person(name, metadata=None):
    return execute_write("INSERT INTO people (name, metadata) VALUES (?, ?)", (name, metadata))

def get_person(person_id):
    return execute_read_one("SELECT * FROM people WHERE id = ?", (person_id,))

def get_person_by_name(name):
    return execute_read_one("SELECT * FROM people WHERE name = ?", (name,))

def list_people():
    return execute_read_all("SELECT * FROM people ORDER BY name")

def update_person(person_id, name, metadata=None):
    return execute_write("UPDATE people SET name = ?, metadata = ? WHERE id = ?", (name, metadata, person_id))

def delete_person(person_id):
    return execute_write("DELETE FROM people WHERE id = ?", (person_id,))