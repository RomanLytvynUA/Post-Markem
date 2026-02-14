from db import get_db

def init_db():
    conn = get_db()
    with open('db/schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database initialized")

if __name__ == "__main__":
    init_db()