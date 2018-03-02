from rest_framework import serializers

from teams.models import  Attendance, Message
from locations.models import UserLocation

class AttendanceSerializer(serializers.ModelSerializer):
    message_id = serializers.CharField(max_length=40)

    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = ('created', 'updated')


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = '__all__'
        read_only_fields = ('created', 'updated')

class MessageUpdateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=16, read_only=True)

    class Meta:
        model = Message
        fields = ("status", "id")

def parse_message(data):
    result = {}
    message = data.get('message')
    if not message:
        return (None, "Message not found")

    id = message.get('@id')
    status = Message.STATUS_SENT

    delivery = message.get('delivery')
    if delivery:
        status = Message.STATUS_DELIVERED
        id = delivery.get("#text")

    read = message.get('read')
    if read:
        status = Message.STATUS_READ
        id = read.get("#text")
    
    result['id'] = id
    result['status'] = status
    result['target'] = message.get('@to').replace('@localhost', '')
    result['sender'] = message.get('@from').replace('@localhost/Rooster', '')
    result['team'] = message.get('team', {}).get('@id')
    result['body'] = message.get('body')
    result['thread'] = message.get('thread')
    result['original'] = data.get('original')
    return (result, None)
