from rest_framework import serializers
from .models import Group, GroupMembership

from accounts.serializers import UserSerializer

class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        exclude = ('members',)
        read_only_fields = ('created_by', 'created', 'updated', 'team')

class GroupMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)

    class Meta:
        model = GroupMembership
        exclude = ('created_by',)
        read_only_fields = ('created', 'updated', 'group', 'user')
        depth = 1

