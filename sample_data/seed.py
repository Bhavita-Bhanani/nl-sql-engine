"""
seed.py — Creates a rich e-commerce SQLite database for the NL-SQL Engine demo.
Run from the sample_data directory:  python seed.py
"""

import sqlite3
import random
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "ecommerce.db")

# ── Seed data ────────────────────────────────────────────────────────────────

FIRST_NAMES = [
    "Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Henry",
    "Isabella", "James", "Karen", "Liam", "Mia", "Noah", "Olivia", "Peter",
    "Quinn", "Rachel", "Samuel", "Tina", "Uma", "Victor", "Wendy", "Xander",
    "Yara", "Zane", "Aisha", "Brian", "Chloe", "Derek",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Martinez", "Wilson", "Anderson", "Taylor", "Thomas", "Jackson",
    "White", "Harris", "Martin", "Thompson", "Young", "Lee", "Walker",
    "Hall", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Adams",
]
CITIES = [
    ("New York", "USA"), ("Los Angeles", "USA"), ("Chicago", "USA"),
    ("Houston", "USA"), ("London", "UK"), ("Manchester", "UK"),
    ("Toronto", "Canada"), ("Vancouver", "Canada"), ("Sydney", "Australia"),
    ("Melbourne", "Australia"), ("Berlin", "Germany"), ("Munich", "Germany"),
    ("Paris", "France"), ("Lyon", "France"), ("Tokyo", "Japan"),
    ("Osaka", "Japan"), ("Dubai", "UAE"), ("Singapore", "Singapore"),
    ("Mumbai", "India"), ("Delhi", "India"),
]
TIERS = ["bronze", "silver", "gold"]

PRODUCTS = [
    ("Wireless Headphones", "Electronics", 89.99, "SoundTech Inc"),
    ("Gaming Mouse", "Electronics", 49.99, "PeriphX"),
    ("Mechanical Keyboard", "Electronics", 129.99, "PeriphX"),
    ("USB-C Hub", "Electronics", 39.99, "TechLink"),
    ("Monitor Stand", "Furniture", 59.99, "DeskPro"),
    ("Standing Desk", "Furniture", 349.99, "DeskPro"),
    ("Office Chair", "Furniture", 249.99, "ErgoSeat"),
    ("Laptop Sleeve", "Accessories", 24.99, "CoverCo"),
    ("Phone Stand", "Accessories", 14.99, "CoverCo"),
    ("Webcam HD", "Electronics", 79.99, "VisionTech"),
    ("LED Desk Lamp", "Home", 34.99, "BrightHome"),
    ("Bluetooth Speaker", "Electronics", 59.99, "SoundTech Inc"),
    ("Notebook Set", "Stationery", 12.99, "PaperWorks"),
    ("Pen Organiser", "Stationery", 9.99, "PaperWorks"),
    ("Whiteboardmarker Set", "Stationery", 7.99, "PaperWorks"),
    ("Yoga Mat", "Fitness", 29.99, "FitGear"),
    ("Resistance Bands", "Fitness", 19.99, "FitGear"),
    ("Water Bottle", "Fitness", 16.99, "HydroMax"),
    ("Backpack", "Accessories", 69.99, "TravelPro"),
    ("Travel Pillow", "Accessories", 22.99, "TravelPro"),
    ("Screen Cleaner Kit", "Accessories", 8.99, "CoverCo"),
    ("Cable Management Kit", "Accessories", 11.99, "TechLink"),
    ("Smart Plug", "Electronics", 19.99, "SmartHome"),
    ("LED Strip Lights", "Home", 26.99, "BrightHome"),
    ("Air Purifier", "Home", 119.99, "CleanAir"),
    ("Coffee Maker", "Home", 89.99, "BrewMaster"),
    ("Protein Powder", "Fitness", 39.99, "FitGear"),
    ("Running Shoes", "Fitness", 79.99, "SpeedFoot"),
    ("Sunglasses", "Accessories", 44.99, "StyleWear"),
    ("Portable Charger", "Electronics", 34.99, "TechLink"),
]

REVIEW_COMMENTS = [
    "Great product, exactly as described!",
    "Really happy with this purchase.",
    "Good quality for the price.",
    "Fast shipping, works perfectly.",
    "Highly recommend to anyone.",
    "Build quality could be better.",
    "Decent product but overpriced.",
    "Not what I expected.",
    "Stopped working after a week.",
    "Absolutely love it, will buy again.",
    "Perfect for my needs.",
    "Solid and durable.",
    "Nice design but flimsy material.",
    "Customer support was helpful.",
    "Average product, nothing special.",
]

ORDER_STATUSES = ["pending", "shipped", "delivered", "cancelled"]


def random_date(start_days_ago: int, end_days_ago: int = 0) -> str:
    delta = random.randint(end_days_ago, start_days_ago)
    d = datetime.now() - timedelta(days=delta)
    return d.strftime("%Y-%m-%d")


def random_datetime(start_days_ago: int, end_days_ago: int = 0) -> str:
    delta = random.randint(end_days_ago, start_days_ago)
    d = datetime.now() - timedelta(days=delta, hours=random.randint(0, 23), minutes=random.randint(0, 59))
    return d.strftime("%Y-%m-%d %H:%M:%S")


def build_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ── Create tables ────────────────────────────────────────────────────────
    cur.executescript("""
        CREATE TABLE customers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            city        TEXT,
            country     TEXT,
            joined_date TEXT,
            tier        TEXT DEFAULT 'bronze'
        );

        CREATE TABLE products (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT NOT NULL,
            category       TEXT,
            price          REAL NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            supplier       TEXT
        );

        CREATE TABLE orders (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id  INTEGER NOT NULL,
            order_date   TEXT NOT NULL,
            status       TEXT DEFAULT 'pending',
            total_amount REAL DEFAULT 0,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        CREATE TABLE order_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id    INTEGER NOT NULL,
            product_id  INTEGER NOT NULL,
            quantity    INTEGER NOT NULL,
            unit_price  REAL NOT NULL,
            FOREIGN KEY (order_id)  REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE reviews (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            product_id  INTEGER NOT NULL,
            rating      INTEGER NOT NULL,
            comment     TEXT,
            created_at  TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_id)  REFERENCES products(id)
        );
    """)

    # ── Seed customers (50) ──────────────────────────────────────────────────
    customers = []
    emails_used = set()
    for i in range(50):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        name = f"{fn} {ln}"
        base_email = f"{fn.lower()}.{ln.lower()}"
        email = f"{base_email}@example.com"
        # ensure uniqueness
        suffix = 1
        while email in emails_used:
            email = f"{base_email}{suffix}@example.com"
            suffix += 1
        emails_used.add(email)
        city, country = random.choice(CITIES)
        joined = random_date(1095, 30)  # 1-3 years ago
        tier = random.choices(TIERS, weights=[50, 35, 15])[0]
        customers.append((name, email, city, country, joined, tier))

    cur.executemany(
        "INSERT INTO customers (name, email, city, country, joined_date, tier) VALUES (?,?,?,?,?,?)",
        customers,
    )
    print(f"Inserted {len(customers)} customers")

    # ── Seed products (30) ───────────────────────────────────────────────────
    products = []
    for name, category, price, supplier in PRODUCTS:
        stock = random.randint(0, 200)
        products.append((name, category, price, stock, supplier))

    cur.executemany(
        "INSERT INTO products (name, category, price, stock_quantity, supplier) VALUES (?,?,?,?,?)",
        products,
    )
    print(f"Inserted {len(products)} products")

    # ── Seed orders (200) ────────────────────────────────────────────────────
    order_rows = []
    for _ in range(200):
        customer_id = random.randint(1, 50)
        order_date = random_date(365, 1)
        status = random.choices(
            ORDER_STATUSES, weights=[10, 20, 60, 10]
        )[0]
        order_rows.append((customer_id, order_date, status, 0.0))

    cur.executemany(
        "INSERT INTO orders (customer_id, order_date, status, total_amount) VALUES (?,?,?,?)",
        order_rows,
    )
    print(f"Inserted {len(order_rows)} orders")

    # ── Seed order_items (500) ───────────────────────────────────────────────
    item_rows = []
    order_totals = {}
    for order_id in range(1, 201):
        num_items = random.randint(1, 5)
        product_ids = random.sample(range(1, 31), min(num_items, 30))
        for pid in product_ids:
            qty = random.randint(1, 4)
            unit_price = PRODUCTS[pid - 1][2]
            item_rows.append((order_id, pid, qty, unit_price))
            order_totals[order_id] = order_totals.get(order_id, 0) + qty * unit_price

    cur.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?,?,?,?)",
        item_rows,
    )
    print(f"Inserted {len(item_rows)} order items")

    # Update order totals
    for order_id, total in order_totals.items():
        cur.execute(
            "UPDATE orders SET total_amount = ? WHERE id = ?",
            (round(total, 2), order_id),
        )

    # ── Seed reviews (150) ───────────────────────────────────────────────────
    review_rows = []
    seen_combos = set()
    attempts = 0
    while len(review_rows) < 150 and attempts < 1000:
        attempts += 1
        cid = random.randint(1, 50)
        pid = random.randint(1, 30)
        if (cid, pid) in seen_combos:
            continue
        seen_combos.add((cid, pid))
        rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 15, 40, 30])[0]
        comment = random.choice(REVIEW_COMMENTS)
        created = random_datetime(300, 1)
        review_rows.append((cid, pid, rating, comment, created))

    cur.executemany(
        "INSERT INTO reviews (customer_id, product_id, rating, comment, created_at) VALUES (?,?,?,?,?)",
        review_rows,
    )
    print(f"Inserted {len(review_rows)} reviews")

    conn.commit()
    conn.close()
    print(f"\n✅ Database created at: {DB_PATH}")
    print("\nSample questions to try:")
    print("  • Show me the top 5 customers by total spending")
    print("  • Which products have low stock (less than 20)?")
    print("  • What is the average order value by country?")
    print("  • Show monthly sales totals for the last 6 months")
    print("  • Which product category generates the most revenue?")
    print("  • Who are our gold tier customers?")
    print("  • What is the average product rating per category?")


if __name__ == "__main__":
    build_database()
