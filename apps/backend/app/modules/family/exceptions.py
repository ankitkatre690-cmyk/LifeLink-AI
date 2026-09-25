class FamilyNotFound(Exception):
    pass


class FamilyAlreadyExists(Exception):
    pass


class FamilyMemberAlreadyExists(Exception):
    pass


class FamilyMemberNotFound(Exception):
    pass


class FamilyMemberUserNotFound(Exception):
    pass


class FamilySelfMembershipNotAllowed(Exception):
    pass
