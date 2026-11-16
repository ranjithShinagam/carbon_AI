from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "carbon_app.db"

print("=" * 70)
print("DATABASE CHECK")
print("=" * 70)

print("Database path:")
print(DB_PATH)

if not DB_PATH.exists():
    print("\n❌ Database does not exist!")
    exit()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(prediction_history)")
columns = cursor.fetchall()

print("\nPredictionHistory columns:\n")

for column in columns:
    print(f"  {column[1]} ({column[2]})")

required = [
    "renewable_energy",
    "nonrenewable_energy",
    "carbon_intensity",
    "energy_per_employee",
    "renewable_energy_ratio",
    "nonrenewable_energy_ratio",
]

column_names = {column[1] for column in columns}

print("\nRequired columns:\n")

for column in required:
    if column in column_names:
        print(f"  ✅ {column}")
    else:
        print(f"  ❌ {column}")

conn.close()