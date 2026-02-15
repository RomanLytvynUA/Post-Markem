from .utilities import execute_write, execute_read_one, execute_read_all

def create_entry(category_id, number, partner1_id, partner2_id=None, metadata=None):
    return execute_write("INSERT INTO entries (category_id, number, partner1_id, partner2_id, metadata) VALUES (?, ?, ?, ?, ?)", 
                         (category_id, number, partner1_id, partner2_id, metadata))

def get_entry(entry_id):
    return execute_read_one("SELECT * FROM entries WHERE id = ?", (entry_id,))

def list_entries(category_id):
    return execute_read_all("SELECT * FROM entries WHERE category_id = ? ORDER BY number", (category_id,))

def get_entry_details(round_id):
    query = """
        SELECT e.number, p1.name as p1_name, p2.name as p2_name
        FROM entries e
        JOIN rounds r ON r.category_id = e.category_id
        JOIN people p1 ON e.partner1_id = p1.id
        LEFT JOIN people p2 ON e.partner2_id = p2.id
        WHERE r.id = ?
        ORDER BY e.number
    """
    return execute_read_all(query, (round_id,))

def get_raw_round_entries(round_id):
    query = """
        SELECT e.number, p1.name as p1_name, p2.name as p2_name
        FROM entries e
        JOIN rounds r ON r.category_id = e.category_id
        JOIN people p1 ON e.partner1_id = p1.id
        LEFT JOIN people p2 ON e.partner2_id = p2.id
        WHERE r.id = ?
        ORDER BY e.number
    """
    return execute_read_all(query, (round_id,))

def get_entries_display_map(round_id):
    rows = get_raw_round_entries(round_id)
    couples = {}
    for row in rows:
        p2 = f" & {row['p2_name']}" if row['p2_name'] else ""
        couples[row['number']] = f"{row['p1_name']}{p2}"
    return couples

def delete_entry(entry_id):
    return execute_write("DELETE FROM entries WHERE id = ?", (entry_id,))