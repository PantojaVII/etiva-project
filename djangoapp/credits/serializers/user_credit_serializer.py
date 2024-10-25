from rest_framework import serializers
from ..models import UserCredit


class UserCreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCredit
        fields = ['user', 'balance', 'created_at', 'updated_at']

class UserCreditSerializerNoUser(serializers.ModelSerializer):
    class Meta:
        model = UserCredit
        fields = ['balance', 'created_at', 'updated_at']


 