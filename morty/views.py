from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser

from .parsers import XmlParser
from .permissions import IsSuperUser
from .serializers import AttendanceSerializer, UserLocationSerializer, parse_message

from accounts.models import User
from teams.models import Team, Message
from teams.serializers import TeamMembershipSerializer, MessageSerializer


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, IsSuperUser))
def get_chats(request, team_id, user_id, format=None):
    team = get_object_or_404(Team, id=team_id)
    user = get_object_or_404(User, id=user_id)
    chat_members = team.get_chat_targets(user)
    serializer = TeamMembershipSerializer(chat_members, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, IsSuperUser))
def set_user_location(request, format=None):
    serializer = UserLocationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response()

    return Response(data=serializer.errors, status=400)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, IsSuperUser))
def set_user_attendance(request, format=None):
    serializer = AttendanceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response()

    return Response(data=serializer.errors, status=400)
        

@api_view(['POST'])
@parser_classes((XmlParser,))
@permission_classes((permissions.IsAuthenticated, IsSuperUser))
def add_or_update_message(request, format=None):
    message_data, error = parse_message(request.data)
    if not message_data:
        return Response(data=error, status=400)

    message = Message.objects.filter(id=message_data.get('id'))
    if message:
        serializer = MessageSerializer(message, message_data)
    else:
        serializer = MessageSerializer(data=message_data)

    if serializer.is_valid():
        serializer.save()
        return Response()

    return Response(data=serializer.errors, status=400)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, IsSuperUser))
def update_message(request, id, format=None):
    message = get_object_or_404(Message, id=id)
    serializer = MessageSerializer(message, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response()

    return Response(data=serializer.errors, status=400)