from rest_framework.permissions import BasePermission
from common.Constant.role_constants import RoleTypeConst


class IsAdminUserRole(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated and
            request.user.role == RoleTypeConst.ADMIN.value
        )