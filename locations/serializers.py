import datetime

from rest_framework import serializers

from .models import UserLocation, LocationStatus, PhoneStatus

from accounts.serializers import UserSerializer


class UserLocationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserLocation
        fields = '__all__'
        exclude = ('team', )
        read_only_fields = ('created', 'updated')


class LocationStatusSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = LocationStatus
        fields = '__all__'
        exclude = ('team', )
        read_only_fields = ('created', 'updated')


class PhoneStatusSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PhoneStatus
        fields = '__all__'
        exclude = ('team', )
        read_only_fields = ('created', 'updated')
