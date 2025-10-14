from rest_framework import permissions


class IsCustomerUser(permissions.BasePermission):
    message = "Only customer users may perform this action."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and hasattr(user, "profile")
            and user.profile.type == "customer"
        )


class IsBusinessUser(permissions.BasePermission):
    message = "Only business users may perform this action."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and hasattr(user, "profile")
            and user.profile.type == "business"
        )


class IsAdminUser(permissions.BasePermission):
    message = "Only admin users may perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )
