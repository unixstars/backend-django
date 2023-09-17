from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import SingletonModel
from .serializers import AppConfigurationSerializer
from .permissions import IsStaff


class AppConfigurationView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        app_config = SingletonModel.load()
        serializer = AppConfigurationSerializer(app_config)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        app_config = SingletonModel.load()
        serializer = AppConfigurationSerializer(app_config, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        app_config = SingletonModel.load()
        serializer = AppConfigurationSerializer(app_config, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
