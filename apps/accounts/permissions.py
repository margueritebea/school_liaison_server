from rest_framework.permissions import BasePermission

class IsParent(BasePermission):
    """
    Permet l'accès uniquement aux utilisateurs ayant le rôle de parent.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == 'parent'

class IsAgent(BasePermission):
    """
    Permet l'accès uniquement aux utilisateurs ayant le rôle d'agent.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == 'agent'