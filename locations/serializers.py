import datetime

from rest_framework import serializers

from .models import UserLocation


class UserLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserLocation
        fields = '__all__'
        read_only_fields = ('created', 'updated')
