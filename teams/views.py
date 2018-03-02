from datetime import datetime
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser

from loco import utils
from loco.services import cache

from . import constants
from .models import Team, TeamMembership, Checkin, CheckinMedia, Message
from .serializers import TeamSerializer, TeamMembershipSerializer, CheckinSerializer,\
    UserMediaSerializer, CheckinMediaSerializer, serialize_events, MessageSerializer, TYPE_LAST_LOCATION
from .permissions import IsTeamMember, IsAdminOrReadOnly, IsAdmin, IsMe

from accounts.models import User
from accounts.serializers import UserSerializer
from notifications.tasks import send_checkin_gcm_async

class TeamList(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None):
        memberships = TeamMembership.objects.filter(user=request.user).exclude(status=constants.STATUS_REJECTED)
        serializer = TeamMembershipSerializer(memberships, many=True)
        return Response(data=serializer.data)

    def post(self, request, format=None):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            team = serializer.save(created_by=request.user)
            return Response(serializer.data)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeamDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsTeamMember, IsAdminOrReadOnly)

    def get(self, request, team_id, format=None):
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        data = TeamSerializer(team).data
        if team.is_admin(request.user):
            data['code'] = team.code
            
        return Response(data=data)

    def put(self, request, team_id, format=None):
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        serializer = TeamSerializer(team, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, team_id, format=None):
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        team.delete()
        return Response(status=204)

class TeamMembershipList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsTeamMember, IsAdminOrReadOnly)

    def get(self, request, team_id, format=None):
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        memberships = TeamMembership.objects.filter(team=team).exclude(status=constants.STATUS_REJECTED)
        serializer = TeamMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    def post(self, request, team_id, format=None):
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)

        phone = request.data.get('phone')

        if not utils.validate_phone(phone):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get_or_create_dummy(phone)
        membership = team.add_member(user, request.user)
        if membership:
            serializer = TeamMembershipSerializer(membership)
            return Response(serializer.data)

        return Response({})


@api_view(['PUT'])
@permission_classes((permissions.IsAuthenticated,))
def join_team(request, format=None):
    team = get_object_or_404(Team, code=request.data.get('code'))
    membership = team.add_member(request.user, request.user)
    if membership:
        serializer = TeamMembershipSerializer(membership)
        return Response(serializer.data)

    return Response(status=status.HTTP_400_BAD_REQUEST)

class TeamMembershipDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdmin)

    def put(self, request, membership_id, format=None):
        membership = get_object_or_404(TeamMembership, id=membership_id)
        self.check_object_permissions(self.request, membership)
        serializer = TeamMembershipSerializer(membership, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, membership_id, format=None):
        membership = get_object_or_404(TeamMembership, id=membership_id)
        self.check_object_permissions(self.request, membership)
        membership.delete()
        return Response(status=204)

class TeamMemberDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdminOrReadOnly)

    def get(self, request, team_id, user_id, format=None):
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        return Response(data=serializer.data)

class TeamMembershipStatus(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def put(self, request, team_id, format=None):
        membership = get_object_or_404(TeamMembership, user=request.user, team=team_id)
        self.check_object_permissions(self.request, membership)
        membership.accept()
        serializer = TeamMembershipSerializer(membership)
        return Response(data=serializer.data)

    def delete(self, request, team_id, format=None):
        membership = get_object_or_404(TeamMembership, user=request.user, team=team_id)
        self.check_object_permissions(self.request, membership)
        membership.reject()
        serializer = TeamMembershipSerializer(membership)
        return Response(status=204)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_chats(request, team_id, format=None):
    team = get_object_or_404(Team, id=team_id)
    # permissions
    if not team.is_member(request.user):
        return Response(status=403)

    chat_members = team.get_chat_members(request.user)
    serializer = TeamMembershipSerializer(chat_members, many=True)
    return Response(serializer.data)

class CheckinList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsTeamMember)
    #TODO permissions not complete

    def add_media(self, checkin, media):
        if media and isinstance(media, list):
            uuids = [m.get('unique_id') for m in media if m.get('unique_id')]
            media = CheckinMedia.objects.filter(unique_id__in=uuids)
            checkin.media.add(*media)

    def get(self, request, team_id, format=None):
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        checkins = team.checkin_set.all()
        serializer = CheckinSerializer(checkins, many=True)
        return Response(serializer.data)

    def post(self, request, team_id, format=None):
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        serializer = CheckinSerializer(data=request.data)

        if serializer.is_valid():
            checkin = serializer.save(team=team, user=request.user)
            media = request.data.get('media')
            self.add_media(checkin, media)
            send_checkin_gcm_async.delay(checkin.id)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CheckinDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdmin, IsMe)

    def get(self, request, team_id, checkin_id, format=None):
        checkin = get_object_or_404(Checkin, id=checkin_id, team=team_id)
        self.check_object_permissions(request, checkin)
        serializer = CheckinSerializer(checkin)
        return Response(serializer.data)

    def put(self, request, team_id, checkin_id, format=None):
        checkin = get_object_or_404(Checkin, id=checkin_id, team=team_id)
        self.check_object_permissions(request, checkin)
        serializer = CheckinSerializer(checkin, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, team_id, checkin_id, format=None):
        checkin = get_object_or_404(Checkin, id=checkin_id, team=team_id)
        self.check_object_permissions(request, checkin)
        checkin.delete()
        return Response(status=204)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, ))
@parser_classes((MultiPartParser,))
def media_upload(request):
    serializer = UserMediaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data)
    else:
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, ))
@parser_classes((MultiPartParser,))
def checkin_media_upload(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if not team.is_member(request.user):
        return Response(status=403)

    serializer = CheckinMediaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, team=team)
        return Response(serializer.data)
    else:
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsTeamMember)

    def get(self, request, team_id, format=None):
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        date = utils.get_query_date(request)
        if date:
            events = team.get_visible_events_by_date(request.user, date)
        else:
            start, limit = utils.get_query_start_limit(request)
            events = team.get_visible_events_by_page(request.user, start, limit)

        data = serialize_events(events)
        return Response(data)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_user_events(request, team_id, user_id, format=None):
    team = get_object_or_404(Team, id=team_id)
    if not team.is_admin(request.user):
        return Response(status=403)

    add_last_location = False
    user = team.members.get(id=user_id)
    date = utils.get_query_date(request)

    if date:
        events = team.get_visible_events_by_date(user, date)
        if date == datetime.now().date():
            add_last_location = True
    else:
        start, limit = utils.get_query_start_limit(request)
        events = team.get_visible_events_by_page(user, start, limit)
        if start in [0, '0']:
            add_last_location = True

    data = serialize_events(events)
    if add_last_location:
        last_location = cache.get_user_last_location(user.id)
        if last_location:
            last_location['type'] = TYPE_LAST_LOCATION
            data.insert(0, last_location)

    return Response(data)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, ))
@parser_classes((MultiPartParser,))
def user_media_upload(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if not team.is_member(request.user):
        return Response(status=403)

    serializer = UserMediaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, team=team)
        return Response(serializer.data)
    else:
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessagesList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsTeamMember)

    def get(self, request, team_id, thread_id, format=None):
        PARAM_START = 'start'
        PARAM_LIMIT = 'limit'
        start = request.query_params.get(PARAM_START)
        start = start or datetime.now()
        limit = request.query_params.get(PARAM_LIMIT, 10)

        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        messages = Message.objects.filter(
            thread=thread_id, created__lt=start).order_by('-created')[:10]
        serializer = MessageSerializer(messages, many=True)
        return Response(data=serializer.data)