import json, requests, polyline
from datetime import datetime

from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView

from loco import utils as loco_utils
from loco.services import cache

from . import utils
from .filters import is_noise, is_pitstop
from .models import UserLocation
from .serializers import UserLocationSerializer

from accounts.models import User
from teams.models import Team, TeamMembership
from teams.permissions import IsTeamMember, IsAdminOrReadOnly, IsAdminOrMe
from morty.services import subscribe_location, unsubscribe_location

def get_snapped_mp(locations, loc_type):
    if loc_type == 'mp':
        url = 'https://api.mapbox.com/matching/v5/mapbox/driving/{0}?access_token=pk.eyJ1Ijoicm9oaXQ3NzciLCJhIjoiY2o4cXA2bG1zMHM0ajJ3bjNydG9nOHpwMiJ9.WhA9bgtcw570J68P_5YIoQ'
    else:
        url = 'http://localhost:5000/match/v1/driving/{0}'

    results = {
        'original': [(l.latitude, l.longitude) for l in locations]
    }

    locations = [str(l.longitude)+','+str(l.latitude) for l in locations]
    path = ";".join(locations)
    query = url.format(path)
    response = requests.get(query)
    response = response.json()

    response = response.get('matchings', [])
    if response:
        matching = response[0]
        matching = polyline.decode(matching['geometry'])
        results['matching'] = [{"lat": r[0], "lng": r[1]} for r in matching]

    # response = response.get('matchings', [])
    # for matching in response:
    #     results += polyline.decode(matching['geometry'])

    # results = [{"lat": r[0], "lng": r[1]} for r in results]

    return results

def snap_mp(locations, loc_type='mp'):
    results = []
    for i in range(0, len(locations), 50):
        sample = locations[i:(i+50)-2]
        results.append(get_snapped_mp(sample, loc_type))
    return results

def new_user_maps(request):
    uid = request.GET.get('uid')
    start = request.GET.get('start')
    end = request.GET.get('end')
    locations = list(UserLocation.objects.filter(user_id=uid, timestamp__gte=start, timestamp__lte=end))
    filtered_locations = []

    for i in range(1, len(locations)):
        filtered_locations.append(locations[i])
        if not is_noise(locations[i], locations[i-1]):
            filtered_locations.append(locations[i])


    # snapped_locations_mp = snap_mp(filtered_locations)
    snapped_locations_os = snap_mp(filtered_locations)
    snapped_locations_os_or = snapped_locations_os
    snapped_locations_os = json.dumps(snapped_locations_os)


    len_locations = len(filtered_locations)
    filtered_locations = json.dumps([(l.latitude, l.longitude) for l in filtered_locations])

    context = {
        'locations': filtered_locations, 
        # 'snapped_locations_mp': snapped_locations_mp,
        'snapped_locations_os': snapped_locations_os,
        'snapped_locations_os_or': snapped_locations_os_or,
        'len_locations': len_locations, 
    }
    return render_to_response('maps.html', context)

def raw_user_maps(request):
    uid = request.GET.get('uid')
    start = request.GET.get('start')
    end = request.GET.get('end')
    filter_noise = request.GET.get('filter_noise', False)
    filter_dis = float(request.GET.get('filter_dis', 0.1))
    locations = list(UserLocation.objects.filter(user_id=uid, timestamp__gte=start, timestamp__lte=end))
    filtered_locations = [locations[0]]

    for i in range(1, len(locations)):
        l = locations[i]
        if filter_noise and not is_noise(l, locations[i-1]):
            filtered_locations.append(l)
        elif not filter_noise:
            filtered_locations.append((l.latitude, l.longitude, l.accuracy, is_pitstop(l, filtered_locations[-1])))

    last_location = filtered_locations[0]
    last_valid_location = filtered_locations[0]
    final_locations = [(last_location.latitude, last_location.longitude, last_location.accuracy, False, 0)]
    pitstops = []
    for l in filtered_locations[1:]:
        if is_pitstop(l, last_location):
            # if l.accuracy < 25:
            # if not pitstops:
            #     pitstops.append(final_locations.pop())

            pitstops.append(l)
                # last_valid_location = final_locations[-1]
                # if last_valid_location[2] > 25:
                #     final_locations.append((l.latitude, l.longitude, l.accuracy, False, 0))
                # else:
                #     midpoint = utils.get_midpoint(l.latitude, l.longitude, last_valid_location[0], last_valid_location[1], last_valid_location[4])
                #     final_locations.append((midpoint[0], midpoint[1], l.accuracy, True, last_valid_location[4]+1))
            pass
            # if l.accuracy < 25:
            #     midpoint = utils.get_midpoint(l.latitude, l.longitude, last_valid_location.latitude, last_valid_location.longitude)
            #     # final_locations.append((l.latitude, l.longitude, l.accuracy, True))
            #     final_locations.append((midpoint[0], midpoint[1], l.accuracy, True))
        else:
            if pitstops:
                final_locations.append(utils.get_midpoint(pitstops))
                pitstops = []
                
            final_locations.append((l.latitude, l.longitude, l.accuracy, False, 0))
        last_location = l


    len_locations = len(final_locations)

    context = {
        'locations': json.dumps(final_locations),
        'filtered_locations': final_locations, 
        'len_locations': len_locations, 
    }
    return render_to_response('maps_raw.html', context)

class LocationSubscriptionList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsTeamMember, IsAdminOrReadOnly)

    def put(self, request, team_id, format=None):
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        user_ids = request.data.get('user_ids', [])
        users = team.members.filter(id__in=user_ids)
        subscribe_location(request.user, users)
        locations = cache.get_users_last_location([u.id for u in users])
        locations = [l for l in locations if l]
        return Response(locations)

    def delete(self, request, team_id, format=None):
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        user_ids = request.data.get('user_ids', [])
        users = team.members.filter(id__in=user_ids)
        unsubscribe_location(request.user, users)
        return Response()

class UserLocationList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdminOrMe)

    def get(self, request, team_id, user_id, format=None):
        membership = get_object_or_404(TeamMembership, team=team_id, user=user_id)
        self.check_object_permissions(self.request, membership)

        date = loco_utils.get_query_date(request, datetime.now().date())
        user = membership.user
        locations = user.userlocation_set.filter(timestamp__date=date)
        if not locations:
            return Response({'polyline': ''})

        first_location = utils.flatten_location(locations[0])
        filtered_locations = [first_location]
        last_valid_location = locations[0]
        pitstops = []
        for i in range(1, len(locations)):
            test_location = locations[i]
            last_location = locations[i-1]

            if is_noise(test_location, last_location):
                continue

            if is_pitstop(test_location, last_valid_location):
                if not pitstops:
                    pitstops.append(filtered_locations.pop())

                pitstops.append(utils.flatten_location(test_location))
            else:
                if pitstops:
                    midpoint = utils.aggregate_stop_points(pitstops)
                    filtered_locations.append(midpoint)
                    pitstops = []
                filtered_locations.append(utils.flatten_location(test_location))
            
            last_valid_location = test_location

        if pitstops:
            midpoint = utils.aggregate_stop_points(pitstops)
            filtered_locations.append(midpoint)
            pitstops = []

        polyline = utils.to_polyline(filtered_locations)
        return Response({'polyline': polyline})
