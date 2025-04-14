from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from django.contrib.auth import get_user_model, login
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from app.user.serializers import UserCreateSerializer, UserDisplaySerializer, UserLoginSerializer, UserUpdateSerializer

# Create your views here.
class UserLogin(GenericAPIView):
    """ View: User login """

    @swagger_auto_schema(
        request_body=
        openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
        )
    )
    def post(self, request):
        user_login_serializer = UserLoginSerializer(data=request.data)
        user_login_serializer.is_valid(raise_exception=True)
        user = user_login_serializer.validated_data['user']

        login(request, user)

        refresh = RefreshToken.for_user(user)
        user_display_serializer = UserDisplaySerializer(user)

        return_data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_display_serializer.data,
        }

        return Response(return_data, status=status.HTTP_200_OK)


class UserLogout(GenericAPIView):
    """ View: User logout """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({}, status=status.HTTP_200_OK)
        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)


class UserRegister(GenericAPIView):
    """ View: Create a user """

    @swagger_auto_schema(
        request_body=
        openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Phone'),
                'date_of_birth': openapi.Schema(type=openapi.TYPE_STRING, description='Date of Birth'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
        )
    )
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            user = get_user_model().objects.get(pk=serializer.data['pk'])

            user_display_serializer = UserDisplaySerializer(user)

            return Response(user_display_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(GenericAPIView):
    """ View: Retrieve, Update, and Delete a user """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user_object = get_user_model().objects.filter(pk=request.user.id, is_active=True).first()
        if user_object == None:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserDisplaySerializer(user_object)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body=
        openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Phone'),
                'date_of_birth': openapi.Schema(type=openapi.TYPE_STRING, description='Date of Birth'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
        )
    )
    def patch(self, request):

        user_object = get_user_model().objects.filter(pk=request.user.id, is_active=True).first()
        if user_object == None:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserUpdateSerializer(user_object, data=request.data, context={'pk': request.user.id}, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Only update password if the field has a value
            if request.data.get('password'):
                user_object.set_password(request.data.get('password'))
                user_object.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):

        user_object = get_user_model().objects.filter(pk=request.user.id, is_active=True).first()
        if user_object == None:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        
        user_object.email=str(user_object.pk)+"--"+user_object.email
        user_object.phone=(str(user_object.pk)+"0"*10)[:10]

        user_object.is_active = False
        user_object.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)
