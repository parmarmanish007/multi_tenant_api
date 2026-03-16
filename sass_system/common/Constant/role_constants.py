from enum import Enum
from common.Constant.constant_helper import ConstantHelper


class RoleTypeConst(ConstantHelper, Enum):
    """ Type constant enumeration """
    ADMIN = "Admin"
    MEMBER = "Member"
