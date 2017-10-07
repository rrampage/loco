from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser

from loco import utils

from . import constants
from .models import Team, TeamMembership, Checkin
from .serializers import TeamSerializer, TeamMembershipSerializer, CheckinSerializer,\
 AttendanceSerializer, UserMediaSerializer, CheckinMediaSerializer
from .permissions import IsTeamMember, IsAdminOrReadOnly, IsAdmin, IsMe

from accounts.models import User

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
        serializer = TeamSerializer(team)
        return Response(data=serializer.data)

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
        print ("This failed", phone)

        if not utils.validate_phone(phone):
            print ("This failed", phone)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get_or_create_dummy(phone)
        membership = team.add_member(user, request.user)

        #Notifiy User

        if membership:
            serializer = TeamMembershipSerializer(membership)
            return Response(serializer.data)

        return Response(data={"errors": "Membership exists"}, status=status.HTTP_400_BAD_REQUEST)

class TeamMembershipDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdmin)

    def put(self, request, membership_id, format=None):
        membership = get_object_or_404(TeamMembership, id=membership_id)
        self.check_object_permissions(self.request, membership)
        serializer = TeamMembershipSerializer(membership, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, membership_id, format=None):
        membership = get_object_or_404(TeamMembership, id=membership_id)
        self.check_object_permissions(self.request, membership)
        membership.delete()
        return Response(status=204)

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
        serializer.save(user=request.user, team=team_id)
        return Response(serializer.data)
    else:
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AttendanceList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsTeamMember)

    def get(self, request, team_id, format=None):
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        attendance = request.user.attendance_set.all()
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

    def post(self, request, team_id, format=None):
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        serializer = AttendanceSerializer(data=request.data)

        if serializer.is_valid():
            attendance = serializer.save(team=team, user=request.user)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_user_attendance(request, team_id, user_id, format=None):
    team = get_object_or_404(Team, id=team_id)
    if not team.is_admin(request.user):
        return Response(status=403)

    user = team.members.get(id=user_id)
    attendance = user.attendance_set.all()
    serializer = AttendanceSerializer(attendance, many=True)
    return Response(serializer.data)

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