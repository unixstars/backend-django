from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import AppConfiguration
from user.models import User
from .serializers import AppConfigurationSerializer
from .permissions import IsStaffOrReadOnly, IsStaff
from rest_framework_simplejwt.tokens import RefreshToken


class AppConfigurationView(APIView):
    permission_classes = [IsStaffOrReadOnly]

    def get(self, request):
        app_config = AppConfiguration.get_instance()
        serializer = AppConfigurationSerializer(app_config)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        app_config = AppConfiguration.get_instance()
        serializer = AppConfigurationSerializer(app_config, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        app_config = AppConfiguration.get_instance()
        serializer = AppConfigurationSerializer(app_config, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetTokenForStaffView(APIView):
    permission_classes = [IsStaff]  # 강력한 접근 제한

    def get(self, request, email, format=None):
        try:
            user = User.objects.get(email=email)
            refresh = RefreshToken.for_user(user)
            return Response(
                {"access": str(refresh.access_token), "refresh": str(refresh)}
            )
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
