from rest_framework import serializers
from ..models import ServiceUsage
from utils.common import *
from .service_serializer import ServiceNoDescriptionSerializer

class ServiceUsageSerializer(serializers.ModelSerializer):
    service = ServiceNoDescriptionSerializer(read_only=True)
    pk_service = serializers.CharField(read_only=True)
    class Meta:
        model = ServiceUsage
        # Liste todos os campos manualmente, exceto o 'user'
        fields = ['id', 'service', 'credits_used', 'used_at', 'pk_service']


class ServiceUsageSerializerNoId(serializers.ModelSerializer):

    service = ServiceNoDescriptionSerializer(read_only=True)

    class Meta:
        model = ServiceUsage
        # Liste todos os campos manualmente, exceto o 'user'
        fields = ['id', 'service', 'credits_used', 'used_at']
