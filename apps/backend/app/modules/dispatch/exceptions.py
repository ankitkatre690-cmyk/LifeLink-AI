class DispatchError(Exception):
    pass


class DispatchNotFound(Exception):
    pass


class EmergencyNotFound(Exception):
    pass


class NoAvailableResponder(Exception):
    pass


class NoAvailableHospitalResource(Exception):
    pass


class DispatchAlreadyExists(Exception):
    pass
