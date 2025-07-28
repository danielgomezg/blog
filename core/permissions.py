from rest_framework import permissions
from django.conf import settings


class HasValidAPIKey(permissions.BasePermission):
    """
    Custom permission to check if a valid API-Key is provided in the request
    """

    def has_permission(self, request, view):
        api_key = request.headers.get("API-Key") #asi debe estar en los headres en las peticiones
        print(api_key)
        return api_key in getattr(settings, "VALID_API_KEYS", [])