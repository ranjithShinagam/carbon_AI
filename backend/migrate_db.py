import sqlite3
from pathlib import Path

# Always use the database located beside this script
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "carbon_app.db"

print("=" * 70)
print("CARBON AI DATABASE MIGRATION")
print("=" * 70)

print(f"Database path:")
print(DB_PATH)

if not DB_PATH.exists():
    print("\n❌ Database does not exist!")
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check current columns
cursor.execute("PRAGMA table_info(prediction_history)")
rows = cursor.fetchall()

existing_columns = {row[1] for row in rows}

print("\nExisting columns:")
for column in existing_columns:
    print(f"  ✓ {column}")

# Columns required by the NEW PredictionHistory model
columns_to_add = {
    "renewable_energy": "REAL NOT NULL DEFAULT 0.0",
    "nonrenewable_energy": "REAL NOT NULL DEFAULT 0.0",
    "carbon_intensity": "REAL NOT NULL DEFAULT 0.0",
    "energy_per_employee": "REAL NOT NULL DEFAULT 0.0",
    "renewable_energy_ratio": "REAL NOT NULL DEFAULT 0.0",
    "nonrenewable_energy_ratio": "REAL NOT NULL DEFAULT 0.0",
}

print("\nChecking required columns...\n")

for column_name, column_definition in columns_to_add.items():

    if column_name in existing_columns:
        print(f"✓ {column_name} already exists")

    else:
        sql = f"""
        ALTER TABLE prediction_history
        ADD COLUMN {column_name} {column_definition}
        """

        cursor.execute(sql)
        print(f"✅ Added {column_name}")

conn.commit()

# Verify AFTER migration
cursor.execute("PRAGMA table_info(prediction_history)")
final_columns = {row[1] for row in cursor.fetchall()}

print("\n" + "=" * 70)
print("FINAL VERIFICATION")
print("=" * 70)

required_columns = list(columns_to_add.keys())

all_present = True

for column in required_columns:
    if column in final_columns:
        print(f"✅ {column}")
    else:
        print(f"❌ {column}")
        all_present = False

conn.close()

if all_present:
    print("\n🎉 DATABASE MIGRATION SUCCESSFUL")
else:
    print("\n❌ MIGRATION INCOMPLETE")