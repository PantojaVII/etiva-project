from rest_framework import serializers
from ..models import Service

 
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['name', 'description', 'cost_in_credits', 'cost_in_generate', 'profit', 'is_active', 'created_at', 'updated_at']

# Segundo ServiceSerializer sem o campo 'description'
class ServiceNoDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['name', 'cost_in_credits']
