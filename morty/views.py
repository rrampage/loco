from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser

from loco.services import cache

from .parsers import XmlParser
from .permissions import IsSuperUser
from .serializers import AttendanceSerializer, UserLocationSerializer, parse_message, MessageUpdateSerializer

from accounts.models import User
from accounts.serializers import UserSerializer
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
        location = serializer.save()
        data = serializer.data
        data['user'] = UserSerializer(location.user).data
        cache.set_user_location(location.user.id, data)
        return Response()

    return Response(data=serializer.errors, status=400)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, IsSuperUser))
def set_user_attendance(request, format=None):
    serializer = AttendanceSerializer(data=request.data)
    if serializer.is_valid():
        latitude = serializer.validated_data.get('latitude')
        if not latitude:
            return Response()
        
        attendance = serializer.save()

        if attendance.action_type==attendance.ACTION_SIGNIN:
            cache.set_user_status(attendance.user.id, cache.USER_STATUS_SIGNEDIN, True)
        else:
            cache.set_user_status(attendance.user.id, cache.USER_STATUS_SIGNEDOUT)

        return Response()

    return Response(data=serializer.errors, status=400)

class MessageList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsSuperUser)
    parser_classes = (JSONParser, XmlParser)

    def get(self, request, format=None):
        PARAM_TARGET = 'target'
        PARAM_TEAM = 'team'
        PARAM_STATUS = 'status'

        target = request.query_params.get(PARAM_TARGET)
        team = request.query_params.get(PARAM_TEAM)
        status = request.query_params.get(PARAM_STATUS)

        messages = Message.objects.filter(
            target=target, team=team, status=status).order_by('-created')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        message_data, error = parse_message(request.data)
        if not message_data:
            return Response(data=error, status=400)

        message = Message.objects.filter(id=message_data.get('id'))
        if message:
            message = message[0]
            if not message.validate_next_status(message_data.get('status')):
                return Response()

            serializer = MessageUpdateSerializer(message, message_data)
        else:
            serializer = MessageSerializer(data=message_data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=201)

        return Response(data=serializer.errors, status=400)   
