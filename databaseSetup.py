import sqlite3

conn = sqlite3.connect('data.db')

c = conn.cursor()

c.execute("""CREATE TABLE profile (
            id integer NOT NULL PRIMARY KEY,
            balance integer NOT NULL
            )""")