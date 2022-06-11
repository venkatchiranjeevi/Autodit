from django.db import connection
from django.db.models import Q
from rest_framework.response import Response
from AutoditApp.mixins import AuthMixin
from AutoditApp.models import TenantGlobalVariables, TenantDepartment, Roles, FrameworkMaster, TenantFrameworkMaster, \
    ControlMaster
from AutoditApp.dal import DeparmentsData, TenantGlobalVariableData, TenantMasterData, RolesData, GlobalVariablesData, \
    RolePoliciesData, TenantFrameworkData, TennatControlHelpers, PolicyDetailsData, TenantControlMasterData, \
    ControlManagementDetailData, PolicyDepartmentsHandlerData
from AutoditApp.constants import RolesConstant as RC, TENANT_LOGOS_BUCKET, S3_ROOT
from AutoditApp.Admin_Handler.dal import FrameworkMasterData
from .AWSCognito import Cognito
from django.conf import settings
from .models import AccessPolicy
from .Utils import list_of_dict_to_dict
from collections import defaultdict
import boto3
from rest_framework.views import APIView

# Create your views here.
from .core import get_users_by_tenant_id, fetch_data_from_sql_query
from .policy_life_cycle_handler import PolicyLifeCycleHandler


class DepartmentsAPI(AuthMixin):

    def get(self, request):
        departments_data = DeparmentsData.get_department_data()
        return Response(departments_data)

    def post(self, request):
        data = request.data
        user = request.user
        tenant_id = user.tenant_id
        data['tenant_id'] = tenant_id
        role_id = user.role_id
        dep_name = data.get("department_name")
        # TODO check duplicate for code and code cant be duplicate
        dep_code = data.get("code")
        dep_obj, created = DeparmentsData.save_department_data(data)
        access_policy_id = RolePoliciesData.get_acceess_policy_id_by_role_id(role_id)
        existing_policy_dep = user.policy
        departments = existing_policy_dep.get("departments", [])
        existing_policy_dep['departments'] = departments
        AccessPolicy.objects.filter(logid=access_policy_id).update(policy=existing_policy_dep)
        if not created:
            Response({"message": "Department Already Exists", "status": False})

        for each_role in RC.Default_Roles.keys():
            role = {"role_name": "{}_{}".format(dep_code, each_role), "role_code": "{}_{}".format(dep_code,
                                                                                                  RC.Default_Roles.get(
                                                                                                      each_role)),
                    "tenant_id": tenant_id,
                    "role_for": each_role, "departments": [dep_obj.id],
                    "policy_name": dep_name}
            # default_roles.append(role)
            RolesData.save_single_role(role)

        return Response({"message": "Department Inserted Successfully", "status": True})

    def patch(self, request):
        data = request.data
        result = DeparmentsData.update_department_data(data)
        return Response({"message": "Updated Successfully", "status": result})

    def delete(self, request):
        dep_id = request.GET.get("id")
        DeparmentsData.delete_department(dep_id)
        return Response({"message": "Deleted Successfully", "status": True})


class GlobalVariablesAPI(AuthMixin):
    def get(self, request):
        global_variables = GlobalVariablesData()
        return global_variables


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
        data['role_id'] = user.role_id
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
    # # def get(self, request):
    #     roles_data = get_roles_data()
    #     return Response(roles_data)

    def post(self, request):
        data = request.data
        tenant_obj = TenantMasterData.save_tenant_master_data(data)
        return Response({"message": "Tenant details created Successfully", "status": True})


class SettingManagementAPI(AuthMixin):
    def get(self, request):
        user = request.user
        tenant_id = user.tenant_id
        t_global_var_data = TenantGlobalVariables.objects.get(tenant_id=int(tenant_id)).result
        global_varialbles_data = eval(t_global_var_data if t_global_var_data else '{}')
        departments = list(TenantDepartment.objects.filter(tenant_id=int(tenant_id)).values('name', 'code', 'id'))
        tenant_roles = list(
            Roles.objects.filter(tenant_id=int(tenant_id)).values('role_id', 'role_name', 'code', 'department_id'))
        selected_frameworks = TenantFrameworkMaster.objects.filter(is_active=1).filter(tenant_id=int(tenant_id)).values(
            'master_framework_id')
        select_framework_ids = [entry['master_framework_id'] for entry in selected_frameworks]
        total_frameworks = FrameworkMaster.objects.filter(is_active=1).values('id', 'framework_name', 'framework_type',
                                                                              'description')
        framework_details = []
        for det in total_frameworks:
            entry = det
            entry['isSubscribed'] = True if entry['id'] in select_framework_ids else False
            framework_details.append(entry)

        all_users = Cognito.get_all_cognito_users_by_userpool_id(settings.COGNITO_USERPOOL_ID)
        tenant_users = get_users_by_tenant_id(all_users, tenant_id, user.userid)

        return Response({'globalVarialbes': global_varialbles_data,
                         'departments': departments,
                         'frameworkDetails': framework_details,
                         'groups': tenant_roles,
                         'userDetails': tenant_users})

# TODO not using inactive anywhere
class ControlsManagementAPI(APIView):
    def get(self, request):
        user = request.user
        tenant_id = user.tenant_id
        master_framework_id = request.GET.get("framework_id")
        if not master_framework_id:
            return self.get_v2(request)
        result = {}
        selected_controls, tenant_framework_id = TenantFrameworkData.get_tenant_selected_controls(tenant_id, master_framework_id)
        all_controls = ControlMaster.objects.filter(framework_id=int(master_framework_id)).values('id',
                                                                                                  'control_name',
                                                                                                  'control_code',
                                                                                                  'category')
        framework_policy_counts = TenantFrameworkData.get_policy_counts(tenant_framework_id=tenant_framework_id,
                                                                        tenant_id=tenant_id)
        selected_control_ids = selected_controls.keys()
        control_details_list = []
        for control in all_controls:
            opted = False
            control_details = {'master_control_id': control.get('id'), 'control_name': control.get('control_name'),
                               'control_code': control.get('control_code'), 'policies_count': 0}
            if control.get('id') in selected_control_ids:
                selected_con  = selected_controls[control.get('id')]
                control_details['control_name'] = selected_con.get('ControlName')
                control_details['control_code'] = selected_con.get('ControlCode')
                control_details['policies_count'] = framework_policy_counts.get(selected_con.get('tenantControlid'), 0)
                opted = True
            control_details['is_control_selected'] = opted
            control_details_list.append(control_details)
        result['controls'] = control_details_list
        return Response(result)

    def get_v2(self, request):
        # user = request.user
        # tenant_id = user.tenant_id
        tenant_id = 16
        req_framework_id = request.GET.get("framework_id")
        # selected frameworks data
        selected_frameworks = TenantFrameworkData.get_tenant_frameworks(tenant_id, req_framework_id)
        select_master_framework_ids = []
        tenant_framework_ids = []
        for each_framework in selected_frameworks:
            select_master_framework_ids.append(each_framework.get("master_framework_id"))
            tenant_framework_ids.append(each_framework.get("id"))

        # selected controls and master framework data
        control_master = TenantFrameworkData.get_control_masters()

        # Frameworks and controls data (Tenant Framework data)
        selected_controls = TenantControlMasterData.get_tenant_controls_data(tenant_framework_ids)
        selected_controls_data = dict()
        for each_control in selected_controls:
            key = "{}_{}".format(each_control.get("master_framework_id"), each_control.get("master_control_id"))
            selected_controls_data[key] = each_control

        # Policy count from Tenant Hirerachy mapper

        hierarchy_mappings = TenantControlMasterData.get_policies_count_by_tenant_framework_id(tenant_id)
        hierarchy_mappings_data = defaultdict(list)
        for each_hierarchy in hierarchy_mappings:
            key = "{}_{}".format(each_hierarchy.get("tenant_framework_id"), each_hierarchy.get("tenant_control_id"))
            hierarchy_mappings_data[key].append(each_hierarchy.get("tenant_policy_id"))

        final_frameworks_controls = []
        for each_frame in selected_frameworks:
            data = dict()
            data['framework_name'] = each_frame.get("tenant_framework_name")
            tenant_framework_id = each_frame.get("id")
            data['tenant_framework_id'] = tenant_framework_id
            framework_id = each_frame.get("master_framework_id")
            data['master_framework_id'] = framework_id
            controls = []
            for each_control in control_master:
                master_control_id = each_control.get("c_id")
                key = "{}_{}".format(framework_id, master_control_id)
                c_data = dict()
                c_data['master_control_id'] = master_control_id
                c_data['control_name'] = each_control.get("ControlName")
                c_data['control_code'] = each_control.get("ControlCode")
                if key in selected_controls_data.keys():
                    c_data['tenant_control_id'] = selected_controls_data.get(key, {}).get("Tenant_control_Id")
                    c_data['is_control_selected'] = True
                    # c_data['policies_count'] = 4
                else:
                    c_data['is_control_selected'] = False
                    c_data['tenant_control_id'] = None
                    # c_data['policies_count'] = 0

                hierarchy_key = "{}_{}".format(tenant_framework_id, c_data['tenant_control_id'])
                c_data['policies_count'] = len(hierarchy_mappings_data.get(hierarchy_key, []))
                c_data['policy_ids'] = hierarchy_mappings_data.get(hierarchy_key, [])

                controls.append(c_data)

            data['controls'] = controls
            final_frameworks_controls.append(data)
        return Response(final_frameworks_controls)

    def post_v1(self, request):
        data = request.data
        user = request.user.pk
        tenant_id = request.user.tenant_id
        data['tenant_id'] = tenant_id
        data['created_by'] = user
        tenant_control_obj = TenantControlMasterData.save_tenant_controls(data)
        return Response({"status": "Updated Controls Successfully", "data": data,
                         "new_control_id":tenant_control_obj.id if tenant_control_obj else None})

    def post(self, request):
        data = request.data
        tenant_id = request.user.tenant_id
        user_id = request.user.pk
        control_details = data.get('controlDetails', [])
        TennatControlHelpers.control_update_handler(tenant_id, data, user_id)
        return Response({'status': 200, 'data': 'Controls updated successfully'})


class ControlManagementDetailAPI(APIView):

    def get(self, request):
        tenant_id = request.user.tenant_id
        master_framework_id = request.GET.get("master_framework_id")
        master_control_id = request.GET.get("master_control_id")
        tenant_framework_details = ControlManagementDetailData.get_controls_data_by_control_id_framework_id(
                                                       master_control_id, master_framework_id, tenant_id)
        if tenant_framework_details:
            tenant_f_id = tenant_framework_details[0].get("tenant_f_id")
            tenant_c_id = tenant_framework_details[0].get("tenant_c_id")
            hierarchy_data = ControlManagementDetailData.get_policies_by_tenant_framework_id_and_tenant_control_id(
                tenant_f_id, tenant_c_id, tenant_id)
            tenant_framework_details[0]['policies'] = hierarchy_data

        return Response(tenant_framework_details)

    def post(self, request):
        data = request.data
        data['tenant_id'] = request.user.tenant_id
        data['created_by'] = request.user.name
        result = ControlManagementDetailData.save_control_description(data)
        return Response({"status": True, "message": "Updated Successfully"})


class ControlManagementDetailHistoryAPI(APIView):

    def get(self, request):
        tenant_control_id = request.GET.get("id")
        tenant_id = request.user.tenant_id
        history = ControlManagementDetailData.get_control_history(tenant_id, tenant_control_id)
        return Response(history)


class PolicyManagementAPI(AuthMixin):
    def get(self, request):
        # TODO get only those tenant related polices and framworks. if frameworkId is avaialbe then only those framework policies if not else all
        # GET departments of policy and add it in response
        tenant_id = request.user.tenant_id

        policies_data = fetch_data_from_sql_query('select a.tenant_id, a.tenantPolicyName, a.version, '
                                                  'a.editor, a.reviewer, a.approver, a.Departments,a.PolicyReference,'
                                                  ' a.State,b.id as FrameworkId, b.FrameworkName, b.Description '
                                                  'from TenantPolicyManager a'
                                                  ' Inner Join FrameworkMaster b on a.MasterFrameworkId = b.id')
        data = {'policiesData': policies_data}

        selected_frameworks = TenantFrameworkMaster.objects.filter(is_active=1).filter(tenant_id=int(tenant_id)).values(
            'tenant_framework_name',
            'master_framework_id',
            'framework_type',
            'description')
        # TODO need to link with user details and reviewr and editor and approver details
        # TODO get role departments and send all users
        # TODO need to add controls linked and controls opted
        data['frameworkDetails'] = selected_frameworks
        return Response(data)


class ControlsCostomTagsAPI(AuthMixin):
    def get(self, request):
        # TODO tennant_id needs to come from user object
        user = request.user
        tenant_id = user.tenant_id
        cursor = connection.cursor()
        result = cursor.execute('''SELECT hm.Fid, hm.Pid, hm.Cid, fm.FrameworkName, fm.`type` as frameworkType, 
        fm.Description as frameworkDescription, cm.ControlName, cm.Description from HirerecyMapper hm Inner JOIN 
        FrameworkMaster fm on hm.Fid = fm.id Left  JOIN ControlMaster cm on hm.CId = cm.Id ''')
        return Response({'data': 'got success'})



class TenantFrameworkMasterAPI(AuthMixin):

    def get(self, request):
        user = request.user
        tenant_id = user.tenant_id
        framework_details = TenantFrameworkMaster.objects.filter(tenant_id=int(tenant_id)).values('id',
                                                                                                  'tenant_framework_name',
                                                                                                  'master_framework_id',
                                                                                                  'description')
        result = [{'frameworkName': det.get('tenant_framework_name'),
                       'masterFrameworkId': det.get('master_framework_id'),
                       'description': det.get('description')} for det in framework_details]
        return Response(result)

    def post(self, request):
        user = request.user
        tenant_id = user.tenant_id
        framework_ids = request.data.get("framework_ids", [])
        master_frameworks = FrameworkMasterData.get_frameworks_data_by_ids(framework_ids)
        formatted_framework_data = list_of_dict_to_dict(master_frameworks, "id")
        TenantFrameworkData.in_active_tenant_framework_data(tenant_id, framework_ids, formatted_framework_data)

        return Response({"message": "Frameworks Added Successfully", "status": True})


class TenantLogoUploaderAPI(AuthMixin):

    def post(self, request):
        file = request.FILES['image']
        s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_KEY)
        s3_bucket_obj = s3.Bucket(TENANT_LOGOS_BUCKET)
        key_name = request.user.name + ".png"
        s3_bucket_obj.put_object(Key=key_name, Body=file)
        logo_url = S3_ROOT.format(key_name)
        tenant_obj = TenantGlobalVariables.objects.get(tenant_id=request.user.tenant_id)
        tenant_result = eval(tenant_obj.result)
        tenant_result['logo_url'] = logo_url
        tenant_obj.result = tenant_result
        tenant_obj.save()
        return Response({"message": "Logo Uploaded Successfully", "status": True})


class PolicyDetailsAPI(AuthMixin):

    def get(self, request):
        data = request.GET
        policy_id = data.get('policyId')
        user = request.user
        tenant_id = user.tenant_id
        details = PolicyLifeCycleHandler.get_complete_policy_details(int(policy_id), int(tenant_id))
        return Response(details)

class ControlsManagementAPIALl(APIView):

    def get(self, request):
        user = request.user
        tenant_id = user.tenant_id
        req_framework_id = request.GET.get("framework_id")
        # selected frameworks data
        selected_frameworks = TenantFrameworkData.get_tenant_frameworks(tenant_id, req_framework_id)
        select_master_framework_ids = []
        tenant_framework_ids = []
        for each_framework in selected_frameworks:
            select_master_framework_ids.append(each_framework.get("master_framework_id"))
            tenant_framework_ids.append(each_framework.get("id"))

        # selected controls and master framework data
        control_master = TenantFrameworkData.get_control_masters()

        # Frameworks and controls data (Tenant Framework data)
        selected_controls = TenantControlMasterData.get_tenant_controls_data(tenant_framework_ids)
        selected_controls_data = dict()
        for each_control in selected_controls:
            key = "{}_{}".format(each_control.get("master_framework_id"), each_control.get("master_control_id"))
            selected_controls_data[key] = each_control

        # Policy count from Tenant Hirerachy mapper

        hierarchy_mappings = TenantControlMasterData.get_policies_count_by_tenant_id(tenant_id)
        hierarchy_mappings_data = defaultdict(list)
        for each_hierarchy in hierarchy_mappings:
            key = "{}_{}".format(each_hierarchy.get("tenant_framework_id"), each_hierarchy.get("tenant_control_id"))
            hierarchy_mappings_data[key].append(each_hierarchy.get("tenant_policy_id"))

        final_frameworks_controls = []
        for each_frame in selected_frameworks:
            data = dict()
            data['framework_name'] = each_frame.get("tenant_framework_name")
            tenant_framework_id = each_frame.get("id")
            data['tenant_framework_id'] = tenant_framework_id
            framework_id = each_frame.get("master_framework_id")
            data['master_framework_id'] = framework_id
            controls = []
            for each_control in control_master:
                master_control_id = each_control.get("c_id")
                key = "{}_{}".format(framework_id, master_control_id)
                c_data = dict()
                c_data['master_control_id'] = master_control_id
                c_data['control_name'] = each_control.get("ControlName")
                c_data['control_code'] = each_control.get("ControlCode")
                if key in selected_controls_data.keys():
                    c_data['tenant_control_id'] = selected_controls_data.get(key, {}).get("Tenant_control_Id")
                    c_data['is_control_selected'] = True
                    # c_data['policies_count'] = 4
                else:
                    c_data['is_control_selected'] = False
                    c_data['tenant_control_id'] = None
                    # c_data['policies_count'] = 0

                hierarchy_key = "{}_{}".format(tenant_framework_id, c_data['tenant_control_id'])
                c_data['policies_count'] = len(hierarchy_mappings_data.get(hierarchy_key, []))
                c_data['policy_ids'] = hierarchy_mappings_data.get(hierarchy_key, [])

                controls.append(c_data)

            data['controls'] = controls
            final_frameworks_controls.append(data)
        return Response(final_frameworks_controls)


# Fields - id, description, policy variables along with values, configured review cycle,
class PolicyDetailsHandler(AuthMixin):
    def get(self, request):
        data = request.data
        policy_id = data.get('policyId')
        user = request.user
        tenant_id = user.tenant_id
        details = PolicyLifeCycleHandler.get_complete_policy_details(policy_id, tenant_id)
        return Response(details)


    def post(self, request):
        data = request.data
        policy_id = data.get('policyId')
        user = request.user
        tenant_id = user.tenant_id
        updated_policy_data = PolicyLifeCycleHandler.policy_summery_details_handler(data, policy_id)
        updated_policy_data['policy_params'] = PolicyLifeCycleHandler.policy_variables_handler(data, policy_id, tenant_id)
        return Response({"meassage": "Policy Details Updated Successfully", "status": True, "data": updated_policy_data})


class PolicyContentHandler(AuthMixin):
    # def get(self, request):
    #     pass

    def post(self, request):
        data = request.data
        policy_id = data.get('policyId')
        user = request.user
        tenant_id = user.tenant_id
        PolicyLifeCycleHandler.policy_content_details_handler(data, policy_id, tenant_id)
        return Response({"message": "Policy Content updated successfully", "status": True})



class TenantDepartmentUsers(AuthMixin):
    def get(self, request):
        pass

    def post(self, request):
        pass


class PolicyStateHandler(AuthMixin):
    def get(self, request):
        pass

    def post(self, request):
        pass


class PolicyDepartmentsHandler(AuthMixin):
    def get(self, request):
        pass

    def post(self, request):
        data = request.data
        data["tenant_id"] = request.user.tenant_id
        data['created_by'] = request.user.name
        result = PolicyDepartmentsHandlerData.save_policy_department_details(data)
        return Response({"status": result, "message": "Department Added Successfully"})

    def delete(self, request):
        policy_department_id = request.GET.get("tenant_policy_id")
        result = PolicyDepartmentsHandlerData.delete_policy_department(policy_department_id)
        return Response({"status": result, "message": "Department Deleted Successfully"})




