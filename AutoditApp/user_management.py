import json

from rest_framework.views import APIView
from AutoditApp.constants import User_Exist_Exception, PASSWOIRD_POLICY
from AutoditApp.AWSCognito import Cognito
from django.conf import settings
from rest_framework.response import Response
from django.db import connection
from AutoditApp.dal import TenantMasterData, DeparmentsData
from AutoditApp.core import get_policies_by_role
from AutoditApp.mixins import AuthMixin


class UsersList(APIView):

    @staticmethod
    def add_new_user_to_cognito_userpool(new_user_data):
        message, status = "User Signup completed Successfully", True
        role = new_user_data.get("role_id")
        ph_num = new_user_data.get("mobnmbr")
        email = new_user_data.get("email")
        attributes = [
            {"Name": 'custom:role_id', "Value": str([role])},
            {"Name": 'gender', "Value": new_user_data.get("gender", "")},
            {"Name": 'name', "Value": new_user_data.get("name")},
            # {"Name": 'nickname', "Value": new_user_data.get("nickname", "")},
            {"Name": 'custom:tenant_id', "Value": str(new_user_data.get("tenant_id", ""))},
            {"Name": 'custom:first_name', "Value": str(new_user_data.get("FirstName", ""))},
            {"Name": 'custom:last_name', "Value": str(new_user_data.get("LastName", ""))},
            {"Name": 'custom:job_title', "Value": str(new_user_data.get("JobTitle", ""))},
            # {"Name": 'custom:department_id', "Value": new_user_data.get("department_id")}
        ]
        if ph_num and ph_num != "":
            ph_num = "{var1}{var2}".format(var1=Cognito.MOBILE_NUM_PREFIX, var2=new_user_data.get("mobnmbr"))
            attributes.append({"Name": 'phone_number', "Value": ph_num})
        if email:
            attributes.append({"Name": 'email', "Value": new_user_data.get("email")})
            attributes.append({"Name": 'email_verified', "Value": 'false'})
        try:
            response = Cognito.CLIENT.admin_create_user(
                UserPoolId=settings.COGNITO_USERPOOL_ID,
                Username=new_user_data.get("name"),
                UserAttributes=attributes,
                TemporaryPassword=new_user_data.get("password"),
                ForceAliasCreation=True,
                DesiredDeliveryMediums=["EMAIL"])
        except Exception as e:
            if str(e) == User_Exist_Exception:
                message, status = "Username is already exist.Please try with another UserName", False
            elif str(e) == 'An error occurred (InvalidPasswordException) when calling the AdminCreateUser operation:' \
                           ' Password did not conform with password policy: Password must have uppercase characters':
                message, status = "Password did not conform with password policy: " \
                                  "Password must have uppercase characters'",\
                                  False
            else:
                message, status = "User Creation Failed", False
            return message, status

        return message, status

    def get(self, request):
        pass

    def post(self, request):
        new_user_data = request.data
        user = request.user
        tenant_id = user.tenant_id
        new_user_data['tenant_id'] = tenant_id
        message, status = UsersList.add_new_user_to_cognito_userpool(new_user_data)
        return Response({"message": message, "status": status})


class UserProfile(AuthMixin):

    def get(self, request):
        user = request.user
        role_id = user.role_id
        tenant_id = user.tenant_id

        role_policies = get_policies_by_role(role_id) if role_id else []
        screen_policies = []
        tenant_details = TenantMasterData.get_tenant_details(tenant_id)
        department_ids = []
        action_permissions = {}
        for po in role_policies:
            policy = eval(po.get('Policy', '{}'))
            screen_policies += policy.get('views', [])
            department_ids += policy.get("departments", [])
            if policy.get('actionPermissions'):
                action_permissions.update(policy.get('actionPermissions', {}))
        department_details = DeparmentsData.get_department_data(department_ids)
        return Response({"username": user.name,
                         "email": user.email,
                         "mobile_number": user.mobnmbr,
                         "first_name": user.first_name,
                         "last_name": user.last_name,
                         "job_title": user.job_title,
                         "gender": user.gender,
                         "status": user.markedfordeletion,
                         "departments": department_details,
                         "tenantDetails": tenant_details,
                         "role_policies": {'screenPermissions': screen_policies,
                                           'ActionPermissions':action_permissions }
                         })
