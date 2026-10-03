from sqlalchemy.orm import Session

from app.database.models.family_group import FamilyGroup
from app.database.models.family_member import FamilyMember
from app.database.models.user import User


class FamilyRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_family(self, family: FamilyGroup):
        self.db.add(family)
        self.db.commit()
        self.db.refresh(family)
        return family

    def get_family_by_creator(self, user_id):
        return (
            self.db.query(FamilyGroup)
            .filter(FamilyGroup.created_by == user_id)
            .first()
        )

    def get_family_by_id(self, family_id):
        return (
            self.db.query(FamilyGroup)
            .filter(FamilyGroup.id == family_id)
            .first()
        )

    def get_user(self, user_id):
        return self.db.query(User).filter(User.id == user_id).first()

    def update(self):
        self.db.commit()

    def delete_family(self, family: FamilyGroup):
        self.db.delete(family)
        self.db.commit()

    def add_member(self, member: FamilyMember):
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def get_member(self, family_id, user_id):
        return (
            self.db.query(FamilyMember)
            .filter(
                FamilyMember.family_group_id == family_id,
                FamilyMember.user_id == user_id,
            )
            .first()
        )

    def get_members(self, family_id):
        return self.db.query(FamilyMember).filter(FamilyMember.family_group_id == family_id).all()

    def delete_member(self, member: FamilyMember):
        self.db.delete(member)
        self.db.commit()

    def get_member_user_ids_for_creator(self, creator_id):
        family = self.get_family_by_creator(creator_id)
        if family is None:
            return []
        return [member.user_id for member in self.get_members(family.id)]
