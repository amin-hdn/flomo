import sqlite3
import time

import flomo.helpers as helpers


class Tracker:
    def __init__(self):
        path = helpers.get_path("sessions.db")

        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY, tag TEXT, name TEXT, start_time TEXT, end_time TEXT, total_time TEXT)"
        )
        self.conn.commit()

    # TODO: fix the function, use time to generate session_id
    def create_session(self, tag: str, name: str, start_time: str) -> str:
        session_id = ""
        self.cursor.execute(
            "INSERT INTO sessions (id, tag, name, start_time) VALUES (?, ?, ?, ?)",
            (session_id, tag, name, start_time),
        )
        self.conn.commit()
        return session_id

    def update_session(self, session_id: str, end_time: str, total_time: str):
        self.cursor.execute(
            "UPDATE sessions SET end_time = ?, total_time = ? WHERE id = ?",
            (end_time, total_time, session_id),
        )
        self.conn.commit()

    def get_sessions(self):
        self.cursor.execute("SELECT * FROM sessions")
        return self.cursor.fetchall()


if __name__ == "__main__":
    tracker = Tracker()
    tracker.create_table()

    session_id = tracker.create_session("study", "work", "10:00")

    print(tracker.get_sessions())

    tracker.conn.close()
