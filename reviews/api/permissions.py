from rest_framework import permissions


class IsReviewer(permissions.BasePermission):
    message = "You have to be the owner of a review to delete it."

    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user
