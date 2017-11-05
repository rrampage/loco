from rest_framework import serializers

from .models import UserAttendance
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'phone','name', 'email')
        

class UserAttendanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAttendance
        exclude = ('location', 'user')
        read_only_fields = ('created', 'updated')
