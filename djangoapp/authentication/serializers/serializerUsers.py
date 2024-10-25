from rest_framework import serializers
from ..models import User
from ..validators import *
from utils.common import *

class UserSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    password_confirmation = serializers.CharField(write_only=True)
    is_active = serializers.BooleanField(read_only=True)
    pk = serializers.SerializerMethodField(read_only=True)
 
    class Meta:
        model = User
        fields = ['pk', 'username', 'email','old_password', 'password', 'password_confirmation', 'is_active']
    
    def get_pk(self, obj):
        return encode_id(obj.pk)

    
class PasswordResetSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    password_confirmation = serializers.CharField(write_only=True)
    is_active = serializers.BooleanField(read_only=True)
    pk = serializers.SerializerMethodField(read_only=True)
 
    class Meta:
        model = User
        fields = ['pk', 'username', 'email','old_password', 'password', 'password_confirmation', 'is_active']
    
    def get_pk(self, obj):
        return encode_id(obj.pk)

