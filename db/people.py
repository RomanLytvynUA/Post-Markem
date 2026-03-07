from .utilities import execute_write, execute_read_one, execute_read_all

def create_person(name, metadata=None):
    return execute_write("INSERT INTO people (name, metadata) VALUES (?, ?)", (name, metadata))

def get_people():
    query = """
        SELECT 
            p.*,
            (
                SELECT COUNT(e.id) 
                FROM entries e 
                WHERE e.partner1_id = p.id OR e.partner2_id = p.id
            ) AS entries,
            (
                SELECT COUNT(a.id) 
                FROM adjudicators a 
                WHERE a.people_id = p.id
            ) AS adjudicators
        FROM people p;
    """
    return execute_read_all(query)

def get_adjudicators_leaderboard():
    query = """
        SELECT
            p.*,
            COUNT(DISTINCT a.id) AS num_of_records,
            ROUND(AVG(ar.alignment), 4) AS score
        FROM people p
        JOIN adjudicators a 
            ON a.people_id = p.id
        JOIN alignment_records ar 
            ON ar.person_id = p.id
        GROUP BY p.id
        ORDER BY score DESC;
    """

    return execute_read_all(query)

def get_adjudication_records(person_id):
    query = """
        SELECT 
            comp.id AS comp_id, comp.date AS comp_date, comp.name AS comp_name,
            cat.id AS cat_id, cat.name AS cat_name,
            r.id AS round_id, r.type AS round_name
        FROM competitions comp
        JOIN categories cat ON cat.competition_id = comp.id
        JOIN rounds r ON r.category_id = cat.id
        JOIN adjudicators a ON a.round_id = r.id
        WHERE a.people_id = ?
    """
    rows = execute_read_all(query, (person_id,)) 
    
    comps = {}
    
    for row in rows:
        comp_id = row['comp_id']
        cat_id = row['cat_id']
        
        if comp_id not in comps:
            comps[comp_id] = {
                'name': row['comp_name'],
                'date': row['comp_date'],
                'categories': {}
            }
            
        if cat_id not in comps[comp_id]['categories']:
            comps[comp_id]['categories'][cat_id] = {
                'name': row['cat_name'],
                'rounds': [] 
            }
            
        comps[comp_id]['categories'][cat_id]['rounds'].append({
            'id': row['round_id'],
            'name': row['round_name']
        })
        
    return [
        {
            'name': c['name'], 
            'date': c['date'], 
            'categories': list(c['categories'].values())
        } 
        for c in comps.values()
    ]

def get_entry_records(person_id):
    query = """
        SELECT 
            comp.id AS comp_id, comp.date AS comp_date, comp.name AS comp_name,
            cat.name AS cat_name,
            MIN(r.id) AS round_id -- Grabs any valid round_id for the UI link
        FROM competitions comp
        JOIN categories cat ON cat.competition_id = comp.id
        JOIN entries e ON e.category_id = cat.id
        JOIN rounds r ON r.category_id = cat.id
        WHERE e.partner1_id = ? OR e.partner2_id = ?
        GROUP BY comp.id, comp.date, comp.name, cat.id, cat.name
    """
    
    rows = execute_read_all(query, (person_id, person_id)) 
    
    comps = {}
    
    for row in rows:
        comp_id = row['comp_id']
        
        if comp_id not in comps:
            comps[comp_id] = {
                'name': row['comp_name'],
                'date': row['comp_date'],
                'categories': []
            }
            
        comps[comp_id]['categories'].append({
            'name': row['cat_name'],
            'round_id': row['round_id']
        })
        
    return list(comps.values())

def get_person(person_id):
    query = """
        SELECT 
            p.*,
            (SELECT COUNT(id) FROM alignment_records WHERE person_id = p.id) AS num_of_records,
            COALESCE((SELECT ROUND(AVG(alignment), 4) FROM alignment_records WHERE person_id = p.id), 0) AS score
        FROM people p
        WHERE p.id = ?
    """
    return execute_read_one(query, (person_id,))

def get_person_by_name(name):
    return execute_read_one("SELECT * FROM people WHERE name = ?", (name,))

def list_people():
    return execute_read_all("SELECT * FROM people ORDER BY name")

def update_person(person_id, name, metadata=None):
    return execute_write("UPDATE people SET name = ?, metadata = ? WHERE id = ?", (name, metadata, person_id))

def delete_person(person_id):
    return execute_write("DELETE FROM people WHERE id = ?", (person_id,))