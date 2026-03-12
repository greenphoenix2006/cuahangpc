import sqlite3

con = sqlite3.connect("store.db")
c = con.cursor()

# USERS
c.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT,
role TEXT
)
""")

# PRODUCTS
c.execute("""
CREATE TABLE IF NOT EXISTS products(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
description TEXT,
price INTEGER,
image TEXT,
stock INTEGER
)
""")

# ORDERS
c.execute("""
CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
total INTEGER,
date TEXT
payment TEXT
)
""")

# ORDER ITEMS
c.execute("""
CREATE TABLE IF NOT EXISTS order_items(
id INTEGER PRIMARY KEY AUTOINCREMENT,
order_id INTEGER,
product_id INTEGER,
quantity INTEGER
)
""")

# ADMIN
c.execute("""
INSERT OR IGNORE INTO users(username,password,role)
VALUES('admin','admin123','admin')
""")

# PRODUCTS
products=[

("Chuột Logitech G102","Gaming Mouse",250000,r"static\images\Chuột Logitech G102.jpg",20),
("Chuột Logitech G304 Wireless","Wireless Gaming Mouse",850000,r"static\images\Chuột Logitech G304 Wireless.jpg",30),
("Chuột Razer DeathAdder","Gaming Mouse",720000,r"static/images/Chuột Razer DeathAdder.jpg",12),
("Chuột Xiaomi Wireless","Office Mouse",180000,r"static/images/Chuột Xiaomi Wireless.webp",36),
("Chuột Dareu EM908","RGB Gaming Mouse",320000,r"static/images/Chuột Dareu EM908.webp",7),

("Bàn phím cơ Dareu EK87","Mechanical Keyboard",650000,r"static/images/Bàn phím cơ Dareu EK87.png",21),
("Bàn phím cơ Akko 3084","Mechanical Keyboard",1200000,r"static/images/Bàn phím cơ Akko 3084.jpg",9),
("Bàn phím Logitech K120","Office Keyboard",150000,r"static/images/Bàn phím Logitech K120.jpg",8),
("Bàn phím Keychron K2","Wireless Mechanical Keyboard",1800000,r"static/images/Bàn phím Keychron K2.webp",15),
("Bàn phím Rapoo Office","Office Keyboard",280000,r"static/images/Bàn phím Rapoo Office.jpg",28),

("Tai nghe Razer Kraken","Gaming Headset",950000,r"static/images/Tai nghe Razer Kraken.jpg",13),
("Tai nghe Logitech G331","Gaming Headset",780000,r"static/images/Tai nghe Logitech G331.webp",6),
("Tai nghe Dareu EH722","Gaming Headset",420000,r"static/images/Tai nghe Dareu EH722.jpg",31),

("Lót chuột Gaming Size L","Mousepad",90000,r"static/images/Lót chuột Gaming Size L.webp",33),
("Lót chuột RGB","RGB Mousepad",250000,r"static/images/Lót chuột RGB.jpg",11),

("USB Kingston 32GB","USB Storage",120000,r"static/images/USB Kingston 32GB.jpg",2),
("Hub USB 4 cổng","USB Hub",180000,r"static/images/Hub USB 4 cổng.jpg",5),
("Giá đỡ laptop nhôm","Laptop Stand",320000,r"static/images/Giá đỡ laptop nhôm.webp",10)

]

c.executemany(
"INSERT INTO products(name,description,price,image,stock) VALUES(?,?,?,?,?)",
products
)

con.commit()
con.close()

print("Database created!")