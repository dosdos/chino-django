import datetime

from rest_framework.response import Response
from backend import serializers, models, utils, chino_model, emails
from rest_framework import generics, viewsets, status

class AuthUserView(APIView):

    serializer_class = serializers.AuthUserSerializer

    def get(self, request):
        chino_user = chino_model.User.fetch(request.user)

        serializer = serializers.AuthUserSerializer(chino_user)
        return Response(serializer.data)

    def post(self, request):
        serializer = serializers.AuthUserSerializer(data=request.data)
        if serializer.is_valid():

            # Fetch current user data..
            user = chino_model.User.fetch(request.user)

            # Copy all updated attributes..
            for attr in serializer.validated_data:
                setattr(user, attr, serializer.validated_data[attr])

            user.update(request.user)

            ser = serializers.AuthUserSerializer(user)
            return Response(ser.data)

        return Response(serializer.errors,
                        status.HTTP_400_BAD_REQUEST)

    pass
