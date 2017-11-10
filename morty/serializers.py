from rest_framework import serializers
from teams.models import  Attendance

from accounts.serializers import UserSerializer
from teams.serializers import TeamSerializer

class AttendanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = ('created', 'updated')
