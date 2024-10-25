from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from ..models import ServiceUsage, Service
from ..serializers.service_usage_serializer import ServiceUsageSerializer

class ServiceUsageViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for listing, retrieving, and using services (deducting credits).
    """
    queryset = ServiceUsage.objects.all()
    serializer_class = ServiceUsageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter by the logged-in user's usages
        return ServiceUsage.objects.filter(user=self.request.user).order_by('-used_at')

    def create(self, request, *args, **kwargs):
        """
        Handles the POST request to use a service and deduct credits.
        """
        user = request.user
        service_id = request.data.get('service_id')

        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

        credits_used = service.cost_in_credits

        try:
            # Try to register the service usage
            service_usage = ServiceUsage.objects.create(user=user, service=service, credits_used=credits_used)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(service_usage)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
