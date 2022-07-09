import json

from rest_framework.views import APIView
from AutoditApp.constants import User_Exist_Exception, PASSWOIRD_POLICY
from AutoditApp.AWSCognito import Cognito
from django.conf import settings
from rest_framework.response import Response
from django.db import connection
from AutoditApp.dal import TenantMasterData, DeparmentsData
from AutoditApp.core import get_policies_by_role, password_generator
from AutoditApp.mixins import AuthMixin


class UsersList(APIView):
    @staticmethod
    def enable_or_diable_cognito_user(username, enable=None, disable=True):
        result=None
        if enable:
            result = Cognito.CLIENT.admin_enable_user(
                UserPoolId=settings.COGNITO_USERPOOL_ID,
                Username=username
            )
        elif disable:
            result = Cognito.CLIENT.admin_disable_user(
                UserPoolId=settings.COGNITO_USERPOOL_ID,
                Username=username
            )
        return result

    @staticmethod
    def add_new_user_to_cognito_userpool(new_user_data):
        message, status = "User created Successfully", True
        role = new_user_data.get("role")
        ph_num = new_user_data.get("mobnmbr")
        email = new_user_data.get("email")
        attributes = [
            {"Name": 'custom:role_id', "Value": str([role])},
            # {"Name": 'gender', "Value": new_user_data.get("gender", "")},
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
            user_dict = Cognito.CLIENT.list_users(
                UserPoolId=settings.COGNITO_USERPOOL_ID,
                Filter='email^=\"{}\"'.format(str(email).strip())
            )
            if user_dict.get("Users"):
                return "User Email already exist", True


        try:
            response = Cognito.CLIENT.admin_create_user(
                UserPoolId=settings.COGNITO_USERPOOL_ID,
                Username=new_user_data.get("name"),
                UserAttributes=attributes,
                TemporaryPassword= str(new_user_data.get("password", "")) or password_generator(),
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
                message, status = str(e), False
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

    def patch(self, request):
        data = request.data
        update_attributes = []
        user_name = data.get("userName")
        marked_for_deletion = str(data.get("markedForDeletion"))
        if marked_for_deletion and marked_for_deletion in Cognito.CONSTANT_TRUE_VALUE:
            UsersList.enable_or_diable_cognito_user(user_name, disable=True)
        elif marked_for_deletion and marked_for_deletion in Cognito.CONSTANT_FALSE_VALUE:
            UsersList.enable_or_diable_cognito_user(user_name, enable=True)

        role_id = data.get("roleId")
        if role_id:
            update_attributes.append({"Name": 'custom:role_id', "Value": str([role_id])})

            updated_user = Cognito.CLIENT.admin_update_user_attributes(
                UserPoolId=settings.COGNITO_USERPOOL_ID,
                Username=user_name,
                UserAttributes=update_attributes)

        return Response({"status": "Updated Successfully"})


class UserProfile(AuthMixin):

    def get(self, request):
        user = request.user
        role_id = user.role_id
        tenant_id = user.tenant_id

        role_policies = get_policies_by_role(role_id) if role_id else []
        screen_policies = []
        tenant_details = TenantMasterData.get_tenant_details(tenant_id)
        department_ids = []
        action_permissions = []
        for po in role_policies:
            policy = eval(po.get('Policy', '{}'))
            screen_policies += policy.get('views', [])
            department_ids += policy.get("departments", [])
            action_permissions += policy.get('actionPermissions', [])
        department_details = DeparmentsData.get_department_data(tenant_id,department_ids)
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
                                           'actionPermissions': action_permissions }
                         })
