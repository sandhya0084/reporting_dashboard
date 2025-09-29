import sqlite3

db_path = "instance/dashboard.db"  # adjust if your path is different
conn = sqlite3.connect("dashboard.db")
cursor = conn.cursor()

# Add missing columns if they don't exist
try:
    cursor.execute("ALTER TABLE user ADD COLUMN email VARCHAR(120);")
except sqlite3.OperationalError:
    print("Column 'email' already exists")

try:
    cursor.execute("ALTER TABLE user ADD COLUMN is_verified BOOLEAN DEFAULT 0;")
except sqlite3.OperationalError:
    print("Column 'is_verified' already exists")

try:
    cursor.execute("ALTER TABLE user ADD COLUMN verification_code VARCHAR(6);")
except sqlite3.OperationalError:
    print("Column 'verification_code' already exists")

try:
    cursor.execute("ALTER TABLE user ADD COLUMN code_expiry DATETIME;")
except sqlite3.OperationalError:
    print("Column 'code_expiry' already exists")

conn.commit()
conn.close()
print("✅ Table updated successfully!")
