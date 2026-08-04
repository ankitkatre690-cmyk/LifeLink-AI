from app.database.seed import seed_roles
from app.database.session import SessionLocal

db = SessionLocal()

try:
    seed_roles(db)
    print("✅ Roles seeded successfully.")

finally:
    db.close()