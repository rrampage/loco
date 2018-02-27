from django.db import models
from django.conf import settings

from loco.models import BaseModel

from teams.models import Team

def group_photo_path(instance, filename):
    return 'groups/{0}/photos/{1}'.format(instance.id, filename)

class Group(BaseModel):
    name = models.CharField(max_length=60)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='chat_groups', on_delete=models.DO_NOTHING)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        through='GroupMembership',
        through_fields=('group', 'user'),
    )
    photo = models.FileField(upload_to=group_photo_path, blank=True, null=True)

    def add_member(self, user, created_by, role=''):
        if not role:
            role = GroupMembership.ROLE_MEMBER
            
        membership = GroupMembership.objects.filter(group=self, user=user)
        if not membership.exists():
            membership = GroupMembership.objects.create(
                group = self,
                user = user,
                created_by = created_by,
                role = role
            )
        else:
            membership = membership[0]

        return membership

    def save(self, *args, **kwargs):
        newly_created = True
        if self.id:
            newly_created = False

        super(Group, self).save(*args, **kwargs)

        if newly_created:
            self.add_member(self.created_by,
                self.created_by, GroupMembership.ROLE_ADMIN)


    def is_member(self, user):
        return GroupMembership.objects.filter(group=self, user=user).exists()

    def is_admin(self, user):
        return GroupMembership.objects.filter(
            group=self, user=user, role=GroupMembership.ROLE_ADMIN).exists()

class GroupMembership(BaseModel):
    ROLE_MEMBER = 'member'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = (
        (ROLE_MEMBER, 'member'),
        (ROLE_ADMIN, 'admin')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="group_invites", on_delete=models.DO_NOTHING)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_MEMBER)
