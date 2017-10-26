from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser


from .permissions import IsSuperUser
from .serializers import UserLocationSerializer

from accounts.models import User
from teams.models import Team
from teams.serializers import TeamMembershipSerializer


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, IsSuperUser))
def get_chats(request, team_id, user_id, format=None):
    team = get_object_or_404(Team, id=team_id)
    user = get_object_or_404(User, id=user_id)
    chat_members = team.get_chat_members(user)
    serializer = TeamMembershipSerializer(chat_members, many=True)
    return Response(serializer.data)

@api_view(['POSt'])
@permission_classes((permissions.IsAuthenticated, IsSuperUser))
def set_user_location(request, format=None):
    serializer = UserLocationSerializer(data=request.data)
    if serializer.is_valid():
    	serializer.save()
        return Response()

    return Response(data=serializer.errors, status=400)