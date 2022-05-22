import json

from django.shortcuts import render
from django.db import connection

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from .constants import Cognito
from rest_framework import status
from django.conf import settings
from AutoditApp.mixins import AuthMixin
from AutoditApp.models import TenantGlobalVariables, TenantDepartment, Roles, FrameworkMaster, TenantFrameworkMaster, \
    TenantHierarchyMapping

from AutoditApp.dal import DeparmentsData, TenantGlobalVariableData, TenantMasterData, RolesData
from django.db.models import Q
from AutoditApp.constants import RolesConstant as RC


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


class DepartmentsAPI(AuthMixin):

    def get(self, request):
        departments_data = DeparmentsData.get_department_data()
        return Response(departments_data)

    def post(self, request):
        data = request.data
        dep_code = data.get("code")
        DeparmentsData.save_department_data(data)
        default_roles = []

        for each_role in RC.Default_Roles.keys():
            role = {"role_name": "{}_{}".format(dep_code, each_role), "role_code": "{}_{}".format(dep_code,
                                                                            RC.Default_Roles.get(each_role))}
            default_roles.append(role)
        RolesData.save_roles_info(default_roles)

        return Response({"message": "Department Inserted Successfully", "status": True})

    def patch(self, request):
        data = request.data
        result = DeparmentsData.update_department_data(data)
        return Response({"message": "Updated Successfully", "status": result})

    def delete(self, request):
        dep_id = request.GET.get("id")
        DeparmentsData.delete_department(dep_id)
        return Response({"message": "Deleted Successfully", "status": True})


class TenantGlobalVariablesAPI(AuthMixin):

    def get(self, request):
        tenant_id = request.GET.get("tenant_id")
        query = Q()
        if tenant_id:
            query &= Q(id=tenant_id)
        t_global_var_data = TenantGlobalVariableData.get_tenant_global_varialbles(query)
        return Response(t_global_var_data)


    def post(self, request):
        user = request.user
        data = request.data
        tenant_id = user.tenant_id
        data['tenant_id'] = tenant_id
        data['username'] = user.username
        result = TenantGlobalVariableData.save_tenant_global_varialble(data)
        return Response({"message": "Global variable inserted successfully", "status": True})

    def patch(self, request):
        data = request.data
        TenantGlobalVariables.objects.filter(id=data.get("id")).update(data)
        return Response({"message": "Updated Successfully", "status": True})

    def delete(self, request):
        tenant_id = request.GET.get("id")
        TenantGlobalVariables.objects.filter(id=tenant_id).delete()
        return Response({"message": "Deleted Successfully", "status": True})


class RolesAPI(AuthMixin):

    def get(self, request):
        roles_data = RolesData.get_roles_data()
        return Response(roles_data)

    def post(self, request):
        data = request.data
        result = RolesData.save_roles_info([data])
        return Response({{"message": "Roles created  successfully", "status": result}})


class TenantMasterAPI(AuthMixin):
    # def get(self, request):
    #     roles_data = get_roles_data()
    #     return Response(roles_data)

    def post(self, request):
        data = request.data
        tenant_obj = TenantMasterData.save_tenant_master_data(data)
        return Response({"message": "Tenant details created Successfully", "status": True})

class SettingManagementAPI(AuthMixin):
    def get(self, request):
        # TODO tenant_id get it from  session
        tenant_id = request.GET.get("tenant_id")
        t_global_var_data = TenantGlobalVariables.objects.get(tenant_id=int(tenant_id)).result
        global_varialbles_data = eval(t_global_var_data)
        departments = list(TenantDepartment.objects.filter(tenant_id=int(tenant_id)).values('name', 'code'))
        tenant_roles = list(Roles.objects.filter(tenant_id=int(tenant_id)).values('role_name', 'code'))
        selected_frameworks = TenantFrameworkMaster.objects.filter(is_active=1).values('master_framework_id')
        select_framework_ids = [entry['master_framework_id'] for entry in selected_frameworks]
        total_frameworks = FrameworkMaster.objects.filter(is_active=1).values('id', 'framework_name', 'framework_type', 'description')
        framework_details = []
        for det in total_frameworks:
            entry = det
            entry['isSubscribed'] = True if entry['id'] in select_framework_ids else False
            framework_details.append(entry)
        # TODO need to add users details
        users_lists = []

        return Response({'globalVarialbes': global_varialbles_data,
                         'departments': departments,
                         'frameworkDetails': framework_details,
                         'groups': tenant_roles,
                         'userDetails': users_lists})

    def post(self, post):
        # UPDATE
        # 1)Global varialbes
        # 2)Frameworks add or remove.
        # 3)Departments add/remove already url is der use that
        # 4)USERS add and assign department and role --> I dont know
        pass


class ControlsManagementAPI(AuthMixin):

    def get(self, request):
        # TODO change
        tenant_id = request.GET.get("tenant_id")
        cursor = connection.cursor()
        cursor.execute('''SELECT hm.Fid, hm.Pid, hm.Cid, fm.FrameworkName, fm.`type` as frameworkType, 
                fm.Description as frameworkDescription, cm.ControlName, cm.Description, hm.id from HirerecyMapper hm Inner JOIN 
                FrameworkMaster fm on hm.Fid = fm.id Left  JOIN ControlMaster cm on hm.CId = cm.Id ''')
        data = cursor.fetchall()
        selected_controls = TenantHierarchyMapping.objects.filter(tenant_id=int(tenant_id)).values('controller_description',
                                                                                                   'policy_reference',
                                                                                                   'framework_id',
                                                                                                   'controller_id',
                                                                                                   'controller_name',
                                                                                                   'master_hierarchy_id')
        custom_selected_control = {entry['master_hierarchy_id'] : entry for entry in selected_controls}
        final_details = []
        for item in data:
            entry = {'frameworkId':item[0],
                     'principleId': item[1],
                     'controlId': item[2],
                     'frameworkName': item[3],
                     'frameworkType': item[4],
                     'frameworkDescription': item[5],
                     'controlName':item[6],
                     'controlMasterDescription': item[7],
                     'hirarecyId': item[8],
                     'customTags': [],
                     'isControlOpted': False}
            if item[8] in custom_selected_control.keys():
                entry['isControlOpted'] = True
                entry['controlActualDescription'] = custom_selected_control[item[8]]['controller_description']
                entry['policyReference'] = custom_selected_control[item[8]]['policy_reference']
                entry['customTags'] = []
            final_details.append(entry)
        return Response(final_details)

    def post(self, request):
        pass


class PolicyManagementAPI(AuthMixin):
    def get(self, request):

        return Response({'data': 'got success'})

    def post(self, request):
        pass


class ControlsCostomTagsAPI(AuthMixin):
    def get(self, request):
        # TODO tennant_id needs to come from user object
        cursor = connection.cursor()
        result = cursor.execute('''SELECT hm.Fid, hm.Pid, hm.Cid, fm.FrameworkName, fm.`type` as frameworkType, 
        fm.Description as frameworkDescription, cm.ControlName, cm.Description from HirerecyMapper hm Inner JOIN 
        FrameworkMaster fm on hm.Fid = fm.id Left  JOIN ControlMaster cm on hm.CId = cm.Id ''')
        return Response({'data': 'got success'})

    def post(self, request):
        pass






