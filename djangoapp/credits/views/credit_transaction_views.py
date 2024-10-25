from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from ..models import CreditTransaction
from ..serializers.credit_transaction_serializer import CreditTransactionSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def credit_transaction_list(request):
    user = request.user
    transactions = CreditTransaction.objects.filter(user=user).order_by('-created_at')
    serializer = CreditTransactionSerializer(transactions, many=True)
    return Response(serializer.data)
