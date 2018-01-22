from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from loco import utils

from .models import User, UserOtp, UserDump
from .serializers import UserSerializer, UserDumpSerializer

from teams.serializers import TeamMembershipSerializer
from notifications.sms import generate_otp, send_otp


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def getOtp(request, format=None):
    phone = request.data.get('phone')

    if not utils.validate_phone(phone):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    otp = generate_otp()
    # otp = '1234'
    send_otp(phone, otp)
    user = User.objects.get_or_create_dummy(phone)

    UserOtp.objects.create_or_update(user = user, otp=otp)
    return Response() 

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def login_user(request, format=None):
    otp = request.data.get('otp')
    phone = request.data.get('phone')

    if utils.validate_otp(otp) and utils.validate_phone(phone):
        return login_otp(otp, phone)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

def login_otp(otp, phone):
    if (UserOtp.objects.checkOtp(otp, phone)):
        user = User.objects.get(phone=phone)
        if not user.is_active:
            user.activate()

        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        data = UserSerializer(user).data
        data['memberships'] = TeamMembershipSerializer(user.get_memberships(), many=True).data
        data['token'] = token.key
        return Response(data=data)
    else:
        return Response(data={"error": "Invalid OTP"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def validate_authentication(request, format=None):
    return Response()

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def logout_user(request, format=None):

    try:
        Token.objects.get(user=request.user).delete()
    except:
        pass

    try:
        logout(request)
    except:
        pass

    
    return Response()

class UserMeDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (FormParser, MultiPartParser, JSONParser)

    def put(self, request, format=None):
        serializer = UserSerializer(request.user, data=request.data)        
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return Response(data=serializer.data)

class UserDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id, format=None):
        user = get_object_or_404(user, id=id)
        serializer = UserSerializer(user)
        return Response(data=serializer.data)

class UpdateGCMToken(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def put(self, request, format=None):
        user = request.user
        gcm_token = request.data.get('gcm_token')

        if gcm_token:
            user.gcm_token = gcm_token
            user.save()
            return Response()
        else:
            return Response(data={'error', 'gcm_token is required'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        request.user.gcm_token = ''
        request.user.save()
        return Response()

class UserDumpView(APIView):

    def get(self, request, format=None):
        start = request.GET.get('start', 0)
        limit = request.GET.get('limit', 10)

        try:
            start = int(start)
            limit = int(limit)
        except Exception as e:
            start = 0
            limit = 10

        data = UserDump.objects.filter(id__gte=start, id__lte=start+limit)
        serializer = UserDumpSerializer(data, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        if not data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = UserDump.objects.create(data=data)
        return Response(UserDumpSerializer(data).data)


@api_view(['GET'])
def get_download_link(request):
    PLAY_STORE_URL = 'https://play.google.com/store/apps/details?id=com.loco.tracker&referrer='

    team_id = request.GET.get('team')
    if not team_id:
        return HttpResponseRedirect(PLAY_STORE_URL)

    referrer = 'utm_source%3DApp%26utm_medium%3Dinvite%26utm_campaign%3DteamGrowth%26' + \
                'team_id%3D' + str(team_id) + '%26referrer_user%3D0'
    final_url = PLAY_STORE_URL + referrer

    return HttpResponseRedirect(final_url)

