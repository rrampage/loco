from rest_framework import serializers
from loco.services import cache
from .models import User, UserDump


class UserSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'phone','name', 'email', 'latitude', 'longitude', 'status', 'photo')
        read_only_fields = ('id', 'phone', 'latitude', 'longitude', 'status')

    def get_status(self, obj):
    	return cache.get_user_status(obj.id)

class UserDumpSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDump
        fields = '__all__'