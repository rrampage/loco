from rest_framework import permissions


class IsTeamMember(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.is_member(request.user)
    
class IsAdminOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.is_admin(request.user)
    
class IsAdminManagerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.is_admin(request.user) or obj.is_manager(request.user)
    
class IsAdminOrMe(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
    	return obj.team.is_admin(request.user) or obj.user == request.user
    
class IsAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
    	return obj.team.is_admin(request.user)
    
class IsMe(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
    	return obj.team.is_admin(request.user) or obj.user == request.user