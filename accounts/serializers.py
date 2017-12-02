from rest_framework import serializers
from .models import User, UserDump


class UserSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_current_status", read_only=True)

    class Meta:
        model = User
        fields = ('id', 'phone','name', 'email', 'latitude', 'longitude', 'status')
        read_only_fields = ('id', 'phone', 'latitude', 'longitude', 'status')

class UserDumpSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDump
        fields = '__all__'