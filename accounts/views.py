import json, collections, ast, time
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from loco import utils

from .models import User, UserOtp, UserDump
from .serializers import UserSerializer, UserDumpSerializer

from teams.serializers import TeamMembershipSerializer

# from notifications.sms import generate_otp
# from notifications.tasks import send_otp_task


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def getOtp(request, format=None):
    phone = request.data.get('phone')

    if not utils.validate_phone(phone):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # otp = generate_otp()
    otp = '1234'
    # send_otp_task.delay(phone, otp)
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


import json, requests, polyline


def get_snapped_mp(locations, loc_type):
    if loc_type == 'mp':
        url = 'https://api.mapbox.com/matching/v5/mapbox/driving/{0}?access_token=pk.eyJ1Ijoicm9oaXQ3NzciLCJhIjoiY2o4cXA2bG1zMHM0ajJ3bjNydG9nOHpwMiJ9.WhA9bgtcw570J68P_5YIoQ'
    else:
        url = 'http://localhost:5000/match/v1/driving/{0}'

    locations = [str(l.longitude)+','+str(l.latitude) for l in locations]
    path = ";".join(locations)
    query = url.format(path)
    response = requests.get(query)
    results = []
    response = response.json()

    response = response.get('matchings', [])
    response = [polyline.decode(m['geometry']) for m in response]
    for matching in response:
        results.append([{"lat": r[0], "lng": r[1]} for r in matching])

    # response = response.get('matchings', [])
    # for matching in response:
    #     results += polyline.decode(matching['geometry'])

    # results = [{"lat": r[0], "lng": r[1]} for r in results]

    return results

def snap_mp(locations, loc_type='mp'):
    results = []
    for i in range(0, len(locations), 50):
        sample = locations[i:(i+50)-10]
        results += get_snapped_mp(sample, loc_type)
    return results

from locations.filters import is_noise
from locations.models import UserLocation

def new_user_maps(request):
    uid = request.GET.get('uid')
    start = request.GET.get('start')
    end = request.GET.get('end')
    locations = list(UserLocation.objects.filter(user_id=uid, timestamp__gte=start, timestamp__lte=end))
    filtered_locations = []

    for i in range(1, len(locations)):
        filtered_locations.append(locations[i])
        # if not is_noise(locations[i], locations[i-1]):
        #     filtered_locations.append(locations[i])


    # snapped_locations_mp = snap_mp(filtered_locations)
    # snapped_locations_os = snap_mp(filtered_locations, 'os')
    snapped_locations_os = []

    len_locations = len(filtered_locations)
    filtered_locations = json.dumps([(l.latitude, l.longitude) for l in filtered_locations])

    context = {
        'locations': filtered_locations, 
        # 'snapped_locations_mp': snapped_locations_mp,
        'snapped_locations_os': snapped_locations_os,
        'len_locations': len_locations, 
    }
    return render_to_response('maps.html', context)


