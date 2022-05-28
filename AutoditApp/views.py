import json

from django.shortcuts import render
from django.db import connection
from django.conf import settings
from django.db.models import Q
from rest_framework.response import Response
from AutoditApp.mixins import AuthMixin
from AutoditApp.models import TenantGlobalVariables, TenantDepartment, Roles, FrameworkMaster, TenantFrameworkMaster, \
    TenantHierarchyMapping, TenantPolicyManager
from AutoditApp.dal import DeparmentsData, TenantGlobalVariableData, TenantMasterData, RolesData, GlobalVariablesData, \
    RolePoliciesData, FrameworkMasterData, TenantFrameworkData, TennatControlHelpers, PolicyDetailsData
from AutoditApp.constants import RolesConstant as RC, TENANT_LOGOS_BUCKET, S3_ROOT
from .AWSCognito import Cognito
from django.conf import settings
from .models import AccessPolicy
from .Utils import list_of_dict_to_dict
import boto3

from .S3_FileHandler import S3FileHandlerConstant

# Create your views here.
from .core import get_users_by_tenant_id, fetch_data_from_sql_query


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
                                                        RC.Default_Roles.get(each_role)), "tenant_id": tenant_id,
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
        tenant_roles = list(Roles.objects.filter(tenant_id=int(tenant_id)).values('role_id','role_name', 'code', 'department_id'))
        selected_frameworks = TenantFrameworkMaster.objects.filter(is_active=1).filter(tenant_id=int(tenant_id)).values('master_framework_id')
        select_framework_ids = [entry['master_framework_id'] for entry in selected_frameworks]
        total_frameworks = FrameworkMaster.objects.filter(is_active=1).values('id', 'framework_name', 'framework_type', 'description')
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


class ControlsManagementAPI(AuthMixin):

    def get(self, request):
        user = request.user
        tenant_id = user.tenant_id
        cursor = connection.cursor()
        selected_frameworks = TenantFrameworkMaster.objects.filter(is_active=1).values('master_framework_id')
        select_framework_ids = [entry['master_framework_id'] for entry in selected_frameworks]
        # TODO need to change to single query
        controls_query ='''SELECT hm.Fid, hm.Pid, hm.Cid, fm.FrameworkName, fm.`type` as frameworkType, 
                fm.Description as frameworkDescription, cm.ControlName, cm.Description, hm.id from HirerecyMapper hm Inner JOIN 
                FrameworkMaster fm on hm.Fid = fm.id Inner JOIN ControlMaster cm on hm.CId = cm.Id and hm.Fid in {Fids}'''
        if select_framework_ids:
            if len(select_framework_ids) == 1:
                select_framework_ids += select_framework_ids
            controls_query = controls_query.format(Fids=str(tuple(select_framework_ids)))
            cursor.execute(controls_query)
            hirarecy_data = cursor.fetchall()
        else:
            hirarecy_data = tuple()

        custom_selected_control = TennatControlHelpers.get_tenant_selected_control(tenant_id)
        final_details = []
        total_frameworks = FrameworkMaster.objects.filter(is_active=1).values('id',
                                                                              'framework_name',
                                                                              'framework_type',
                                                                              'description')
        framework_details = []
        for det in total_frameworks:
            entry = det
            entry['isSubscribed'] = True if entry['id'] in select_framework_ids else False
            framework_details.append(entry)

        for item in hirarecy_data:
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
                # TODO need to add policy reference
                # entry['policyReference'] = custom_selected_control[item[8]]['policy_reference']
                entry['customTags'] = []
            final_details.append(entry)
        return Response({'controlDetails':final_details, 'frameworkDetails': framework_details})

    def post(self, request):
        data = request.data
        tenant_id = request.user.tenant_id
        control_details = data.get('controlDetails', [])
        control_ids = []
        updated_hirarecy_ids = []
        for entry in control_details:
            control_ids.append(entry.get('controlId'))
            updated_hirarecy_ids.append(entry.get('hirarecyId'))
        all_tenant_controls = TennatControlHelpers.get_tenant_selected_control(tenant_id, 'id', all=True)
        selected_active_controls = []
        selected_inactive_controls = []
        for control in all_tenant_controls.values():
            if control.get('is_active'):
                selected_active_controls.append(control.get('master_hierarchy_id'))
            else:
                selected_inactive_controls.append(control.get('master_hierarchy_id'))

        # selected_hirarecy_ids = custom_selected_control_hid.keys()
        deleted_hirarcy_ids = list(set(selected_active_controls) - set(updated_hirarecy_ids))
        new_hirarecy_insert_ids = list(set(updated_hirarecy_ids) - set(list(all_tenant_controls.keys())))
        hirarecy_in_active_ids = list(set(set(selected_inactive_controls).intersection(set(updated_hirarecy_ids))))
        if deleted_hirarcy_ids:
            TenantHierarchyMapping.objects.filter(master_hierarchy_id__in = deleted_hirarcy_ids).update(is_active=0)
        if hirarecy_in_active_ids:
            TenantHierarchyMapping.objects.filter(master_hierarchy_id__in = hirarecy_in_active_ids).update(is_active=1)
        if new_hirarecy_insert_ids:
            query = '''select hm.id as hirarecyId, hm.Fid as frameworkId, hm.Cid as controlId, cm.ControlName, 
            cm.Description, hm.PolicyId as masterPolicyId  from HirerecyMapper hm Inner Join ControlMaster
             cm on hm.Cid = cm.Id and hm.id in {hirerecy_ids}'''
            if len(new_hirarecy_insert_ids) == 1:
                new_hirarecy_insert_ids += new_hirarecy_insert_ids
            query = query.format(hirerecy_ids=str(tuple(new_hirarecy_insert_ids)))
            new_insertion_data = fetch_data_from_sql_query(query)
            parent_policy_ids = [entry['masterPolicyId'] for entry in new_insertion_data]
            policy_details_query = '''select pm.id, pm.PolicyName, pm.Category, tpm.ParentPolicyID from 
            PolicyMaster pm left Join TenantPolicyManager tpm on tpm.ParentPolicyID = pm.id and 
            tpm.tenant_id =16 where pm.id in {pids}'''
            if len(parent_policy_ids) ==1:
                parent_policy_ids += parent_policy_ids
            policy_details_query = policy_details_query.format(pids=str(tuple(parent_policy_ids)))
            policy_details = fetch_data_from_sql_query(policy_details_query)
            insert_polices = []
            for det in policy_details:

                if not det.get('ParentPolicyID'):
                    insert_polices.append(
                    TenantPolicyManager(tenant_id=int(tenant_id),
                                        tenant_policy_name=det['PolicyName'],
                                        category=det['Category'],
                                        version=1,
                                        policy_reference='',
                                        parent_policy_id=det['id']))
            if insert_polices:
                TenantPolicyManager.objects.bulk_create(insert_polices)

            existing_policy = TenantPolicyManager.objects.filter(parent_policy_id__in=parent_policy_ids).values()
            existing_policy_format = {entry['parent_policy_id']: entry for entry in existing_policy}
            inserts_controls_data = []
            for entry in new_insertion_data:
                inserts_controls_data.append(TenantHierarchyMapping(controller_id=entry.get('controlId', ''),
                                       controller_name=entry.get('ControlName', ''),
                                       controller_description=entry.get('Description'),
                                       tenant_id=int(tenant_id),
                                       master_hierarchy_id=entry.get('hirarecyId'),
                                       category=entry.get('Category'),
                                       tenant_policy_id=existing_policy_format[new_insertion_data[0]['masterPolicyId']]['id'],
                                       is_active=1))
                # TenantHierarchyMapping)
            if inserts_controls_data:
                TenantHierarchyMapping.objects.bulk_create(inserts_controls_data)
        return Response({'status':200, 'data': 'Controls updated successfully'})


class PolicyManagementAPI(AuthMixin):
    def get(self, request):
        tenant_id = request.user.tenant_id
        policies_data = fetch_data_from_sql_query('select a.tenant_id, a.tenantPolicyName, a.version, '
                                                  'a.editor, a.reviewer, a.approver, a.Departments,a.PolicyReference,'
                                                  ' a.State,b.id as FrameworkId, b.FrameworkName, b.Description '
                                                  'from TenantPolicyManager a'
                                                  ' Inner Join FrameworkMaster b on a.MasterFrameworkId = b.id')
        data = {'policiesData': policies_data}

        selected_frameworks = TenantFrameworkMaster.objects.filter(is_active=1).filter(tenant_id=int(tenant_id)).values('tenant_framework_name',
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

    def post(self, request):
        pass


class TenantFrameworkMasterAPI(AuthMixin):

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
        key_name = request.user.name +  ".png"
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
        policy_id = request.GET.get("policy_id")
        get_policy_data = PolicyDetailsData.get_policy_details(6, "autodit-policies")
        return Response({'data': ''})
    #     Step get policy details and editiot, revier and assigner
    # Step2 get control details
    # Step3 get revier
    #


class PolicyStateHandler(AuthMixin):
    def post(self, request):
        pass


class PolicyUsersHandler(AuthMixin):
    def post(self, request):
        pass
