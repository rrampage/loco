import datetime

from rest_framework import serializers

from .models import UserLocation

from accounts.serializers import UserSerializer


class UserLocationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserLocation
        fields = '__all__'
        read_only_fields = ('created', 'updated')
