from rest_framework import serializers
from ..models import CreditTransaction 

 
class CreditTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTransaction
        fields = ['user', 'transaction_type', 'amount', 'created_at', 'description']

class CreditTransactionNoUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTransaction
        fields = ['transaction_type', 'amount', 'created_at', 'description']