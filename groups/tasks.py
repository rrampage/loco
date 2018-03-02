from __future__ import absolute_import, unicode_literals
import json

from celery import shared_task

from loco.services.cache import set_group_members

from .models import GroupMembership

@shared_task
def update_group_members_async(group_id):
    memberships = GroupMembership.objects.filter(group=group_id)
    members = [m.user.id for m in memberships]
    set_group_members(group_id, members)