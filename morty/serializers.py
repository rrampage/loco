import datetime

from rest_framework import serializers

from .models import UserLocation


class UserLocationSerializer(serializers.ModelSerializer):
    timestamp = serializers.IntegerField()

    class Meta:
        model = UserLocation
        fields = '__all__'
        read_only_fields = ('created', 'updated')

    def create(self, validated_data):
        timestamp = validated_data['timestamp']
        timestamp = datetime.datetime.fromtimestamp(timestamp/1000)
        validated_data['timestamp'] = timestamp
        return UserLocation.objects.create(**validated_data)
