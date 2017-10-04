import json, collections, ast, time
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser

from loco import utils

from .models import User, UserOtp, UserDump2
from .serializers import UserSerializer, UserDumpSerializer, UserMediaSerializer

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

class UserDumpView2(APIView):

    def get(self, request, format=None):
        start = request.GET.get('start', 0)
        limit = request.GET.get('limit', 10)

        try:
            start = int(start)
            limit = int(limit)
        except Exception as e:
            start = 0
            limit = 10

        data = UserDump2.objects.filter(id__gte=start, id__lte=start+limit)
        serializer = UserDumpSerializer(data, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        if not data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = UserDump2.objects.create(data=data)
        return Response(UserDumpSerializer(data).data)

class UserDumpJsonP2(APIView):
    def get(self, request, format=None):
        start = request.GET.get('start', 0)
        limit = request.GET.get('limit', 10)
        name = request.GET.get('name', '')

        try:
            start = int(start)
            limit = int(limit)
        except Exception as e:
            start = 0
            limit = 10

        data = UserDump2.objects.filter(id__gte=start, id__lte=start+limit)
        serializer = UserDumpSerializer(data, many=True)
        data = serializer.data

        for d in data:
            if 'data' in d:
                item_data = ast.literal_eval(d['data'])
                d['data'] = item_data

        data = [d for d in data if name.lower() in d['data'].get('user', {}).get('name', '').lower()]
                
        response = 'eqfeed_callback(' + json.dumps((data)) + ')';

        return HttpResponse(response)

def user_pings(request):
    name = request.GET.get('name', '')
    start = request.GET.get('start', '1505466395000')
    end = request.GET.get('end', str(int(time.time()*1000)))
    groupby = request.GET.get('groupby', 'day').lower() #value can be day/hour/min
    data = UserDump2.objects.filter()
    serializer = UserDumpSerializer(data, many=True)
    data = serializer.data
    temp_data = {}
    battery_data = {}
    for d in data:
        if 'data' in d:
            item_data = ast.literal_eval(d['data'])
            d['data'] = item_data
    for d in data:
        try:
            if (int(start) <= d['data'].get('location', {}).get('timestamp', 0) and int(end) >= d['data'].get('location', {}).get('timestamp', 0)):
                if name.lower() in d['data'].get('user', {}).get('name', '').lower():
                    dt = datetime.fromtimestamp(d['data'].get('location', {}).get('timestamp', 0)/1000)
                    if(groupby == "day"):
                        dt = dt.replace( hour=0, minute=0, second=0, microsecond=0)
                    if(groupby == "hour"):
                        dt = dt.replace( minute=0, second=0, microsecond=0)
                    if(groupby == "min"):
                        dt = dt.replace( second=0, microsecond=0)
                    battery_data[str(dt)] = d['data']['battery']

                    if(str(dt) in temp_data):
                        temp_data[str(dt)] += 1
                    else:
                        temp_data[str(dt)] = 1
        except Exception,e:
            pass
    
    g_data = [['Time', 'Pings']]
    b_data = [['Time', 'Battery']]
    if(groupby == "day"):
        start_date = datetime.fromtimestamp(int(start)/1000)
        end_date = datetime.fromtimestamp(int(end)/1000)
        delta = end_date - start_date
        for i in range(delta.days + 1):
            temp_date = (start_date+timedelta(i)).replace( hour=0, minute=0, second=0, microsecond=0)
            g_data.append([ str(temp_date.date()), temp_data.get(str(temp_date)) or 0 ])                           
            b_data.append( [ str(temp_date.date()), battery_data.get(str(temp_date)) or 0 ])
    if(groupby == "hour"):
        start_date = datetime.fromtimestamp(int(start)/1000)
        end_date = datetime.fromtimestamp(int(end)/1000)
        td = (end_date - start_date)
        delta = int(td.total_seconds()/3600)
        for i in range(delta + 1):
            temp_date = (start_date+timedelta(seconds=(3600 * i))).replace(minute=0, second=0, microsecond=0)
            g_data.append([ str(temp_date.hour), temp_data.get(str(temp_date)) or 0 ])                           
            b_data.append( [ str(temp_date.hour), battery_data.get(str(temp_date)) or 0 ])
    if(groupby == "min"):
        start_date = datetime.fromtimestamp(int(start)/1000)
        end_date = datetime.fromtimestamp(int(end)/1000)
        td = (end_date - start_date)
        delta = int(td.total_seconds()/60)
        for i in range(delta + 1):
            temp_date = (start_date+timedelta(seconds=(60 * i))).replace(second=0, microsecond=0)
            g_data.append([ str(temp_date.minute), temp_data.get(str(temp_date)) or 0 ])                           
            b_data.append( [ str(temp_date.minute), battery_data.get(str(temp_date)) or 0 ])


    context = RequestContext(request, {'g_data': g_data , 'b_data': b_data})
    return render_to_response('bars.html', context)

def user_maps(request):
    start = request.GET.get('start', 0)
    limit = request.GET.get('limit', 10)
    name = request.GET.get('name', '')
    
    BASE_URL = '/users/dump21'
    data_url = BASE_URL + '?start={0}&limit={1}&name={2}'.format(start, limit, name)
    context = RequestContext(request, {'data_url': data_url})
    return render_to_response('maps.html', context)


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