from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from AutoditApp.constants import Cognito
from AutoditApp.dal import TenantMasterData, RolesData
from rest_framework import status
from django.conf import settings

from AutoditApp.user_management import UsersList


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


class PasswordChange(APIView):

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        password_response = Cognito.CLIENT.admin_set_user_password(
            UserPoolId=settings.COGNITO_USERPOOL_ID,
            Username=username,
            Password=password,
            Permanent=True
        )
        return Response({"message": "Password Updated Successfully", "status": True})


class SignUp(APIView):

    def post(self, request):
        new_user_data = request.data
        user_name = new_user_data.get("name", "")
        tenant_data = {"tenant_name": user_name}
        tenant_obj = TenantMasterData.save_tenant_master_data(tenant_data)
        role_data = {'role_name': user_name + " ADMIN", "role_code":  user_name + "AD"}
        role_obj = RolesData.save_single_role([role_data])
        # new_user_data['tenant_id'] = tenant_obj.id
        new_user_data['role_id'] = role_obj.role_id
        response = UsersList.add_new_user_to_cognito_userpool(new_user_data)
        return Response({"message": "User registration completed Successfully", "status": True})