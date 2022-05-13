from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from .constants import Cognito
from rest_framework import status
from django.conf import settings


class BaseLogin(APIView):
    login_type_password, login_type_otp = "password", "otp"
    alert_msg = {"message_body": "You have logged in from new device",
                 "message_title": "AviLeap-alert"}

    def authenticate_cognito_users(self, username, password):
        try:
            response = Cognito.CLIENT.admin_initiate_auth(
                UserPoolId=settings.COGNITO_USERPOOL_ID,
                ClientId=settings.COGNITO_APP_CLIENT_ID,
                AuthFlow='ADMIN_USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password,

                }
            )
        except Exception as exe:
            return Response({"detail":
                                 "Username or password did not match"},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(response)


class PasswordLogin(APIView):

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        try:
            response = Cognito.CLIENT.admin_initiate_auth(
                UserPoolId=settings.COGNITO_USERPOOL_ID,
                ClientId=settings.COGNITO_APP_CLIENT_ID,
                AuthFlow='ADMIN_USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password,

                }
            )
        except Exception as exe:
            return Response({"detail":
                                 "Username or password did not match"},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(response)


class PasswordLogin(BaseLogin):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        cognito_code = request.data.get("cognito_code")
        cognito_auth = request.data.get("cognito_auth")
        if cognito_auth:
            return self.authenticate_cognito_users(username, password)

        return self.get_user_data(request, username, password,
                                  self.login_type_password)