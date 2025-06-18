import sqlite3 as sq


def init_db():
    conn = sq.connect('messenger.db')
    curs = conn.cursor()

    # Create Users Table
    curs.execute("""
              CREATE TABLE IF NOT EXISTS users
              (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password_hash TEXT
              )
              """)

    # Create Contacts Table
    curs.execute("""
              CREATE TABLE IF NOT EXISTS contacts
              (
                  user_id INTEGER,
                  contact_id INTEGER,
                  contact_username TEXT,
                  FOREIGN KEY (user_id) REFERENCES users(id),
                  FOREIGN KEY (contact_id) REFERENCES users(id)
              )
              """)

    # Create Messages Table
    curs.execute("""
              CREATE TABLE IF NOT EXISTS messages
              (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  sender_id INTEGER,
                  receiver_id INTEGER,
                  message TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (sender_id) REFERENCES users(id),
                  FOREIGN KEY (receiver_id) REFERENCES users(id)
              )
              """)

    conn.commit()
    conn.close()


def add_user(username, password_hash):
    conn = sq.connect('messenger.db')
    curs = conn.cursor()

    curs.execute("INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
    conn.commit()

    curs.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = curs.fetchone()[0]

    conn.close()

    return user_id


def get_user_id(username):
    conn = sq.connect('messenger.db')
    curs = conn.cursor()

    curs.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = curs.fetchone()

    conn.close()

    return result[0] if result else None


def add_contact(user_id, contact_username):
    contact_id = get_user_id(contact_username)

    if (contact_id):
        conn = sq.connect('messenger.db')
        curs = conn.cursor()

        curs.execute("INSERT OR IGNORE INTO contacts (user_id, contact_id, contact_username) VALUES (?, ?, ?)", (user_id, contact_id, contact_username))
        conn.commit()

        conn.close()

        return True

    return False


def get_contacts(user_id):
    conn = sq.connect('messenger.db')
    curs = conn.cursor()

    curs.execute("SELECT contact_username FROM contacts WHERE user_id = ?", (user_id,))
    contacts = [row[0] for row in curs.fetchall()]

    conn.close()

    return contacts


def store_messages(sender_id, receiver_id, message):
    conn = sq.connect('messenger.db')
    curs = conn.cursor()

    curs.execute("INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)", (sender_id, receiver_id, message))
    conn.commit()

    conn.close()


def get_message_history(user_id, contact_username):
    contact_id = get_user_id(contact_username)

    if not contact_id:
        return []

    conn = sq.connect('messenger.db')
    curs = conn.cursor()

    curs.execute("""
        SELECT u.username, m.message, m.timestamp
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE (m.sender_id = ? AND m.receiver_id = ?) OR (m.sender_id = ? AND m.receiver_id = ?)
        ORDER BY m.timestamp DESC
    """, (user_id, contact_id, contact_id, user_id))

    history = [(row[0], row[1], row[2]) for row in curs.fetchall()]

    conn.close()

    return history


if __name__ == '__main__':
    init_db()