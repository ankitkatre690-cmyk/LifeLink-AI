from sqlalchemy.orm import Session

from app.database.models.role import Role

DEFAULT_ROLES = [
    {
        "name": "Citizen",
        "description": "Normal application user",
    },
    {
        "name": "Family",
        "description": "Family member",
    },
    {
        "name": "Responder",
        "description": "Emergency responder",
    },
    {
        "name": "Hospital",
        "description": "Hospital staff",
    },
    {
        "name": "Police",
        "description": "Police department",
    },
    {
        "name": "Admin",
        "description": "System administrator",
    },
]


def seed_roles(db: Session):
    for role in DEFAULT_ROLES:

        exists = (
            db.query(Role)
            .filter(Role.name == role["name"])
            .first()
        )

        if not exists:
            db.add(Role(**role))

    db.commit()