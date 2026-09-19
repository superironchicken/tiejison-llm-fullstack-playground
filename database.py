import sqlite3


def connect_db():
    conn = sqlite3.connect('test.db')
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = connect_db()
    try:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS CONVERSATIONS(
            ID  INTEGER  PRIMARY KEY  AUTOINCREMENT,
            TITLE  TEXT  NOT NULL,
            CREATE_TIME  TEXT  DEFAULT CURRENT_TIMESTAMP
        );""")
        c.execute("""CREATE TABLE IF NOT EXISTS MESSAGES(
            ID  INTEGER  PRIMARY KEY  AUTOINCREMENT,
            CONVERSATION_ID  INTEGER  NOT NULL,
            ROLE  TEXT  NOT NULL,
            CONTENT  TEXT  NOT NULL,
            CREATE_TIME  TEXT  DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (CONVERSATION_ID) REFERENCES CONVERSATIONS(ID) ON DELETE CASCADE
        );""")
        conn.commit()
    finally:
        conn.close()


def create_conversation(title: str) -> int:
    """新建一个会话，返回它的自增 id。"""
    conn = connect_db()
    try:
        c = conn.cursor()
        c.execute("INSERT INTO CONVERSATIONS (TITLE) VALUES (?)", (title,))
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()


def save_message(conversation_id: int, role: str, content: str):
    """往某个会话里写一条消息。"""
    conn = connect_db()
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO MESSAGES (CONVERSATION_ID, ROLE, CONTENT) VALUES (?, ?, ?)",
            (conversation_id, role, content),
        )
        conn.commit()
    finally:
        conn.close()

def list_conversations():
    conn = connect_db()
    try:
        c = conn.cursor()
        c.execute("SELECT ID, TITLE FROM CONVERSATIONS ORDER BY ID DESC")
        # fetchall 返回的是元组列表，这里转成字典，方便接口直接返回 JSON
        return [{"id": row[0], "title": row[1]} for row in c.fetchall()]
    finally:
        conn.close()


def get_messages(conversation_id: int):
    conn = connect_db()
    try:
        c = conn.cursor()
        c.execute(
            "SELECT ROLE, CONTENT FROM MESSAGES WHERE CONVERSATION_ID = ? ORDER BY ID",
            (conversation_id,),
        )
        return [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    finally:
        conn.close()
