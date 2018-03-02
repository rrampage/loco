from rest_framework import permissions


class IsGroupMember(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.is_member(request.user)
    
class IsGroupAdminOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.is_admin(request.user)
    
class IsGroupAdminOrMe(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
    	return obj.group.is_admin(request.user) or obj.user == request.user
    
class IsGroupAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
    	return obj.group.is_admin(request.user)
    
class CanAlterGroupMembership(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.group.is_admin(request.user):
            return True
        if obj.user == request.user:
            return request.method == "DELETE"

        return False