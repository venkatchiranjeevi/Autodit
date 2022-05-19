from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from .constants import Cognito
from rest_framework import status
from django.conf import settings
from AutoditApp.mixins import AuthMixin
from AutoditApp.models import TenantGlobalVariables
from .core import get_department_data, get_roles_data, save_department_data, update_department_data, delete_department, \
    get_tenant_global_varialbles, save_tenant_global_varialble
from django.db.models import Q


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
            return Response({"message": "Username or password did not match"},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(response)


class Departments(AuthMixin):

    def get(self, request):
        departments_data = get_department_data()
        return Response(departments_data)

    def post(self, request):
        data = request.data
        save_department_data(data)
        return Response({"message": "Department Inserted Successfully", "status": True})

    def patch(self, request):
        data = request.data
        result = update_department_data(data)
        return Response({"message": "Updated Successfully", "status": result})

    def delete(self, request):
        dep_id = request.GET.get("id")
        delete_department(dep_id)
        return Response({"message": "Deleted Successfully", "status": True})


class TenantGlobalVariablesData(AuthMixin):
    def get(self, request):
        tenant_id = request.GET.get("tenant_id")
        query = Q()
        if tenant_id:
            query &= Q(id=tenant_id)
        t_global_var_data = get_tenant_global_varialbles(query)
        return Response(t_global_var_data)

    def post(self, request):
        data = request.data
        result = save_tenant_global_varialble(data)
        return Response({"message": "Global variable inserted successfully", "status": True})

    def patch(self, request):
        data = request.data
        TenantGlobalVariables.objects.filter(id=data.get("id")).update(data)
        return Response({"message": "Updated Successfully", "status": True})

    def delete(self, request):
        tenant_id = request.GET.get("id")
        TenantGlobalVariables.objects.filter(id=tenant_id).delete()
        return Response({"message": "Deleted Successfully", "status": True})


class Roles(AuthMixin):

    def get(self, request):
        roles_data = get_roles_data()
        return Response(roles_data)


class TenantDetails(AuthMixin):
    def get(self, request):
        roles_data = get_roles_data()
        return Response(roles_data)

