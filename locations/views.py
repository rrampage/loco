import json, requests, polyline

from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView

from loco.services import cache

from .filters import is_noise
from .models import UserLocation
from .serializers import UserLocationSerializer

from accounts.models import User
from teams.models import Team
from teams.permissions import IsTeamMember, IsAdminOrReadOnly
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

class LocationSubscriptionList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsTeamMember, IsAdminOrReadOnly)

    def put(self, request, team_id, format=None):
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        user_ids = request.data.get('user_ids', [])
        users = team.members.filter(id__in=user_ids)
        subscribe_location(request.user, users)
        locations = cache.get_users_location([u.id for u in users])
        locations = [l for l in locations if l]
        return Response(locations)

    def delete(self, request, team_id, format=None):
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(self.request, team)
        user_ids = request.data.get('user_ids', [])
        users = team.members.filter(id__in=user_ids)
        unsubscribe_location(request.user, users)
        return Response()