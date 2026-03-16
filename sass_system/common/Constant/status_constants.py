from enum import Enum
from common.Constant.constant_helper import ConstantHelper


class StatusTypeConst(ConstantHelper, Enum):
    """ Type constant enumeration """
    TODO = "Todo"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
