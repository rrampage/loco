from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView

from .models import Group, GroupMembership
from .tasks import update_group_members_async
from .serializers import GroupSerializer, GroupMembershipSerializer
from .permissions import IsGroupMember, IsGroupAdminOrReadOnly, CanAlterGroupMembership

from accounts.models import User
from teams.models import Team, TeamMembership
from teams import permissions as team_permissions

class GroupList(APIView):
    permission_classes = (permissions.IsAuthenticated, team_permissions.IsTeamMember)

    def add_members(self, request, group):
        user_ids = request.data.get('members')
        if not user_ids:
            return

        if not isinstance(user_ids, list):
            user_ids = [user_ids]

        group.add_members(user_ids, request.user)

    def post(self, request, team_id, format=None):
    	team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save(created_by=request.user, team=team)
            self.add_members(request, group)
            return Response(serializer.data)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GroupDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsGroupMember, IsGroupAdminOrReadOnly)

    def get(self, request, group_id, format=None):
        group = get_object_or_404(Group, id=group_id)
        self.check_object_permissions(self.request, group)
        data = GroupSerializer(group).data            
        return Response(data=data)

    def put(self, request, group_id, format=None):
        group = get_object_or_404(Group, id=group_id)
        self.check_object_permissions(self.request, group)
        serializer = GroupSerializer(group, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, group_id, format=None):
        group = get_object_or_404(Group, id=group_id)
        self.check_object_permissions(self.request, group)
        group.delete()
        return Response(status=204)

class GroupMembershipList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsGroupMember, IsGroupAdminOrReadOnly)

    def get(self, request, group_id, format=None):
        group = get_object_or_404(Group, id=group_id)
        self.check_object_permissions(self.request, group)
        memberships = GroupMembership.objects.filter(group=group)
        serializer = GroupMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    def post(self, request, group_id, format=None):
        group = get_object_or_404(Group, id=group_id)
        self.check_object_permissions(self.request, group)
        user_ids = request.data.get('members')
        if not isinstance(user_ids, list):
            user_ids = [user_ids]

        group_memberships = group.add_members(user_ids, request.user)
        if group_memberships:
            update_group_members_async.delay(group_id)
            serializer = GroupMembershipSerializer(group_memberships, many=True)
            return Response(serializer.data)

        return Response({})

class GroupMembershipDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, CanAlterGroupMembership)

    def put(self, request, group_id, membership_id, format=None):
        membership = get_object_or_404(GroupMembership, id=membership_id)
        self.check_object_permissions(self.request, membership)
        serializer = GroupMembershipSerializer(membership, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, group_id, membership_id, format=None):
        membership = get_object_or_404(GroupMembership, id=membership_id)
        self.check_object_permissions(self.request, membership)
        group_id = membership.group.id
        membership.delete()
        update_group_members_async.delay(group_id)
        return Response(status=204)