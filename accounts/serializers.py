from rest_framework import serializers
from .models import User, UserDump2, UserMedia


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'phone','name', 'email', 'latitude', 'longitude')
        read_only_fields = ('id', 'phone', 'latitude', 'longitude')

class UserDumpSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDump2


class UserMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserMedia
        fields = ('media',)