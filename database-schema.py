import sqlite3


# Create database
conn = sqlite3.connect("ecommerce.db")
cursor = conn.cursor()


# ------------------ CREATE TABLES ------------------


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    city TEXT,
    signup_date TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INTEGER PRIMARY KEY,
    supplier_name TEXT,
    country TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    name TEXT,
    category_id INTEGER,
    price REAL,
    supplier_id INTEGER
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    order_date TEXT,
    status TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    amount REAL,
    payment_method TEXT,
    payment_date TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product_id INTEGER,
    rating INTEGER,
    comment TEXT
)
""")


# ------------------ INSERT DATA ------------------


# USERS
cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", [
    (1, "Amit", "amit@gmail.com", "Mumbai", "2023-01-10"),
    (2, "Priya", "priya@gmail.com", "Pune", "2023-02-15"),
    (3, "Rahul", "rahul@gmail.com", "Delhi", "2023-03-20")
])


# CATEGORIES
cursor.executemany("INSERT INTO categories VALUES (?, ?)", [
    (1, "Electronics"),
    (2, "Clothing")
])


# SUPPLIERS
cursor.executemany("INSERT INTO suppliers VALUES (?, ?, ?)", [
    (1, "TechCorp", "India"),
    (2, "FashionHub", "USA")
])


# PRODUCTS
cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", [
    (1, "Laptop", 1, 80000, 1),
    (2, "Phone", 1, 40000, 1),
    (3, "T-Shirt", 2, 1000, 2)
])


# ORDERS
cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", [
    (1, 1, "2024-01-01", "Delivered"),
    (2, 2, "2024-02-01", "Pending")
])


# ORDER ITEMS
cursor.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?)", [
    (1, 1, 1, 1),
    (2, 1, 3, 2),
    (3, 2, 2, 1)
])


# PAYMENTS
cursor.executemany("INSERT INTO payments VALUES (?, ?, ?, ?, ?)", [
    (1, 1, 82000, "UPI", "2024-01-01"),
    (2, 2, 40000, "Card", "2024-02-01")
])


# REVIEWS
cursor.executemany("INSERT INTO reviews VALUES (?, ?, ?, ?, ?)", [
    (1, 1, 1, 5, "Excellent"),
    (2, 2, 2, 4, "Good"),
    (3, 3, 3, 3, "Average")
])


# ------------------ SAVE ------------------


conn.commit()
conn.close()


print("✅ Database created and filled successfully!")
