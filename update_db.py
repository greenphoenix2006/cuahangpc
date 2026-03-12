import sqlite3

con = sqlite3.connect("store.db")
cur = con.cursor()

cur.execute("ALTER TABLE orders ADD COLUMN payment TEXT")

con.commit()
con.close()

print("Database updated!")