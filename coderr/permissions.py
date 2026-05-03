from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, "user", obj)
        return owner == request.user


class IsReviewer(permissions.BasePermission):
    message = "You have to be the owner of a review to delete it."

    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user


class IsCustomerUser(permissions.BasePermission):
    message = "Only customer users may perform this action."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.type == "customer")


class IsBusinessUser(permissions.BasePermission):
    message = "Only business users may perform this action."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.type == "business")


class IsAdminUser(permissions.BasePermission):
    message = "Only admin users may perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_staff
        )
