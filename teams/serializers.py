from rest_framework import serializers
from .models import Team, TeamMembership, Checkin, CheckinMedia, Attendance, UserMedia

from accounts.serializers import UserSerializer

class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        exclude = ('members', )
        read_only_fields = ('created_by', 'created', 'updated')

    def create(self, validated_data):
        return Team.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        return instance

class TeamMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    team = TeamSerializer(read_only=True)

    class Meta:
        model = TeamMembership
        exclude = ('created_by',)
        read_only_fields = ('created', 'updated', 'team', 'user')
        depth = 1

    def create(self, validated_data):
        return Team.objects.create(**validated_data)

class CheckinMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckinMedia
        exclude = ('team', 'user')
        read_only_fields = ('created', 'updated', 'unique_id')

class CheckinSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    media = CheckinMediaSerializer(read_only=True, many=True)

    class Meta:
        model = Checkin
        fields = ('created', 'updated', 'team', 'user', 'description',
         'latitude', 'longitude', 'media')
        read_only_fields = ('created', 'updated', 'team', 'user')

class AttendanceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = ('team','user', 'created', 'updated')

class UserMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMedia
        exclude = ('team', 'user', 'checkin')
        read_only_fields = ('created', 'updated', 'unique_id')


TYPE_CHECKIN = 'checkin'
TYPE_ATTENDANCE = 'attendance'

def serialize_events(events):
    results = []
    for event in events:
        if isinstance(event, Checkin):
            data = CheckinSerializer(event).data
            data['type'] = TYPE_CHECKIN
        elif isinstance(event, Attendance):
            data = AttendanceSerializer(event).data
            data['type'] = TYPE_ATTENDANCE
        else:
            continue

        results.append(data)

    return results
