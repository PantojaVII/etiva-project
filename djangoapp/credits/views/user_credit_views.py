from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from ..models import UserCredit
from ..serializers.user_credit_serializer import UserCreditSerializer
from rest_framework import status

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_credit_detail(request):
    user = request.user
    try:
        user_credit = UserCredit.objects.get(user=user)
    except UserCredit.DoesNotExist:
        return Response({"error": "No credit balance found for the user."}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserCreditSerializer(user_credit)
    return Response(serializer.data)
