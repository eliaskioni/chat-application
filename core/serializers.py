import uuid

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from core.models import MessageModel
from rest_framework.serializers import ModelSerializer, CharField


def send_sms_to_partner(phone_number, text):
    import requests

    url = "http://34.252.86.123:8006/api"
    payload = {
        "request_id": str(uuid.uuid4()),
        "system_generated": "false",
        "callback_url": "/api/sms/sms_callbacks",
        "request_type": "sms",
        "customer_id": phone_number,
        "text": text,
        "partner_guid": "equityguid",
        "chat_message": True
    }
    headers = {
        'content-type': "application/json",
        'authorization': "CdD8KcU6u3J&BDiT",
        'session': "James",
        'cache-control': "no-cache",
        'postman-token': "74e3a84f-272d-f98c-b16c-3d374aabf388"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)


class MessageModelSerializer(ModelSerializer):
    user = CharField(source='user.username', read_only=True)
    recipient = CharField(source='recipient.username')

    def create(self, validated_data):
        user = self.context['request'].user
        recipient = get_object_or_404(
            User, username=validated_data['recipient']['username'])
        msg = MessageModel(recipient=recipient,
                           body=validated_data['body'],
                           user=user)
        msg.save()
        if recipient.username != 'admin':
            send_sms_to_partner(recipient.username, msg.body)
        return msg

    class Meta:
        model = MessageModel
        fields = ('id', 'user', 'recipient', 'timestamp', 'body')


class UserModelSerializer(ModelSerializer):

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        user.set_password(validated_data.get('username'))
        user.save()
        return user

    class Meta:
        model = User
        fields = ('username',)
