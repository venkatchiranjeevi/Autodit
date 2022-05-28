from AutoditApp.models import TenantDepartment as Departments, Roles, TenantGlobalVariables, Tenant, GlobalVariables, \
    RolePolicies, AccessPolicy, FrameworkMaster, TenantFrameworkMaster, TenantHierarchyMapping, TenantPolicyManager, \
    PolicyMaster, ControlMaster, ControlMaster, HirerecyMapper
from django.db.models import Q
from .constants import DEFAULT_VIEWS, EDITIOR_VIEWS
from AutoditApp.AWSCognito import Cognito
from .core import get_policies_by_role
from .S3_FileHandler import S3FileHandlerConstant


class BaseConstant:
    def __init__(self):
        pass


class AccessPolicyData(BaseConstant):
    @staticmethod
    def create_access_policy(role_id):
        pass


class RolesData(BaseConstant):

    @staticmethod
    def get_roles_data():
        roles_data = Roles.objects.all().values("role_id", "role_name", "code")
        return roles_data

    @staticmethod
    def get_role_details(roles_ids):
        query = Q()
        if roles_ids:
            query &= Q(role_id__in=roles_ids)
        roles_data = Roles.objects.filter(query).values("role_id", "role_name", "code")
        return roles_data

    @staticmethod
    def save_roles_info(data):
        roles_instances = []
        for each_role in data:
            role_obj = Roles(role_name=each_role.get("role_name"), code=each_role.get("role_code"),
                             tenant_id=each_role.get("tenant_id"))
            role_obj.save()

        # Roles.objects.bulk_create(roles_instances)

        return True

    @staticmethod
    def save_single_role(data):
        department_id = data.get("departments", [])
        role_obj = Roles(role_name=data.get("role_name"), code=data.get("role_code"), tenant_id=data.get("tenant_id"),
                         department_id=department_id[0] if department_id else None)
        role_obj.save()

        access_policy = AccessPolicy.objects.create(policyname=data.get("policy_name"),
                                                    policy={"views": DEFAULT_VIEWS if data.get('role_for') != 'Editor' else EDITIOR_VIEWS, 'actions': [],
                                                            "departments": data.get("departments", [])},
                                                    type="GENERAL")
        role_policies = RolePolicies.objects.create(role_id=role_obj.role_id, accesspolicy_id=access_policy.logid)

        return role_obj


class RolePoliciesData(BaseConstant):

    @staticmethod
    def get_acceess_policy_id_by_role_id(role_id):
        try:
            access_policy_id = RolePolicies.objects.get(role_id=eval(role_id)[0]).accesspolicy_id
        except:
            return None
        return access_policy_id


class TenantMasterData(BaseConstant):

    @staticmethod
    def get_tenant_details(tenant_id=None):
        query = Q()
        if tenant_id:
            query &= Q(id=tenant_id)
        return Tenant.objects.filter(query).values()

    @staticmethod
    def save_tenant_master_data(data):
        tenant_obj = Tenant.objects.create(name=data.get("tenant_name"), tenant_details=data.get("details"),
                              properties=data.get("properties"))
        TenantGlobalVariables.objects.create(result={'org_name': '', 'org_size': '', 'website_url': '', 'ceo_name': '',
                                    'ceo_email': '', 'cto_name': '', 'cto_email': '', 'logo_url': '', 'primary_email':'',
                                                     'primary_name':""},
                                             tenant_id=tenant_obj.id)
        return tenant_obj


class DeparmentsData(BaseConstant):

    @staticmethod
    def get_department_data(department_ids=[]):
        query = Q()
        if department_ids:
            query = Q(id__in=department_ids)
        department_data = Departments.objects.filter(query).values("id", "name", "code")
        return department_data

    @staticmethod
    def save_department_data(data):
        dep_obj, created = Departments.objects.get_or_create(name=data.get("department_name"), code=data.get("code"),
                                                             tenant_id=data.get("tenant_id"))

        return dep_obj, created

    @staticmethod
    def update_department_data(data):
        department_obj = Departments.objects.get(id=id)
        is_active = data.get("is_active")
        description = data.get("description")
        if is_active:
            department_obj.is_active = is_active
        if description:
            department_obj.description = description
        department_obj.name = data.get("name")
        department_obj.code = data.code("code")
        department_obj.tenant_id = data.get("tenant_id")
        department_obj.save()
        return True

    @staticmethod
    def delete_department(dep_id):
        Departments.objects.filter(id=dep_id).delete()
        return True


class GlobalVariablesData(BaseConstant):
    @staticmethod
    def get_global_variables():
        global_variables = list(GlobalVariables.objects.all().values())
        return global_variables


class TenantGlobalVariableData(BaseConstant):

    @staticmethod
    def get_tenant_global_varialbles(query):
        t_global_var_data = TenantGlobalVariables.objects.filter(query).values()
        return t_global_var_data

    @staticmethod
    def save_tenant_global_varialble(data):
        tbv_obj, created = TenantGlobalVariables.objects.get_or_create(tenant_id=data.get("tenant_id"))
        tbv_obj.result = data.get("globalVarialbes")
        tbv_obj.save()
        roles = data.get("role_id", '[]')
        for each_role in eval(roles):
            role_policies = RolePolicies.objects.filter(role_id=each_role).values()
            for each_policy in role_policies:
                access_policy_obj = AccessPolicy.objects.get(logid=each_policy.get("accesspolicy_id"))
                existing_policy = eval(access_policy_obj.policy)
                existing_policy['globalVarialbes'] = data.get("globalVarialbes")
                access_policy_obj.policy = existing_policy
                access_policy_obj.save()
        # role_policies = get_policies_by_role(role_id=each_role)
        # role_policies[0]["globalVarialbes"] = data.get("globalVarialbes")
        return tbv_obj


class FrameworkMasterData(BaseConstant):

    @staticmethod
    def get_frameworks_data_by_ids(master_ids):
        master_frameworks = list(FrameworkMaster.objects.filter(id__in=master_ids, is_active=True,
                                                                is_deleted=False).values())
        return master_frameworks

    @staticmethod
    def get_framework_master():
        all_frameworks = FrameworkMaster.objects.all().values()
        return all_frameworks

    @staticmethod
    def save_frameworks(data):
        framework_obj = FrameworkMaster(framework_name=data.get("framework_name"),
                                       framework_type=data.get("framework_type"),
                                       description= data.get("Description"), is_deleted=False, is_active=True,
                                       created_by= data.get("created_by"))
        framework_obj.save()
        return framework_obj


class TenantFrameworkData(BaseConstant):

    @staticmethod
    def in_active_tenant_framework_data(tenant_id, tenant_master_ids, new_teanant_framworks):
        tenant_frameworks_objs = TenantFrameworkMaster.objects.filter(tenant_id=tenant_id).update(is_active=False)
        for each_frame in tenant_master_ids:
            master_data = new_teanant_framworks.get(each_frame)
            tenant_obj, created = TenantFrameworkMaster.objects.get_or_create(master_framework_id=master_data.get("id"),
                                                                              tenant_id=tenant_id)
            if created:
                tenant_obj.tenant_framework_name = master_data.get("framework_name")
                tenant_obj.description = master_data.get("description")
                tenant_obj.framework_type = master_data.get("framework_type")
                tenant_obj.is_active = True
            else:
                tenant_obj.is_active = True
            tenant_obj.save()

    @staticmethod
    def create_tenant_frameworks(framworks_data):
        tenant_frame_instancess = []
        for each_frame in framworks_data:
            tenant_frame_obj = TenantFrameworkMaster(tenant_framework_name=each_frame.get("framework_name"),
                                                     description=each_frame.get("description"),
                                                     tenant_id=each_frame.get("tenant_id"),
                                                     master_framework_id=each_frame.get("master_framework_id"),
                                                     framework_type=each_frame.get("framework_type"))
            tenant_frame_instancess.append(tenant_frame_obj)
        result = TenantFrameworkMaster.objects.bulk_create(tenant_frame_instancess)
        return result


class TennatControlHelpers(BaseConstant):

    @staticmethod
    def get_tenant_selected_control(tenant_id, key='master_hierarchy_id', all=False):
        select_controls = TenantHierarchyMapping.objects.filter(tenant_id=int(tenant_id))
        if not all:
            select_controls = select_controls.filter(is_active=1)

        selected_controls = select_controls.values(
            'controller_description',
            'controller_id',
            'controller_name',
            'master_hierarchy_id',
            'tenant_policy_id',
            'id',
            'is_active')
        custom_selected_control = {entry[key]: entry for entry in selected_controls}
        return custom_selected_control


class PolicyDetailsData(BaseConstant):
    @staticmethod
    def get_policy_details(policy_id, tenant_id, bucket):
        result = {}
        tenant_policy_obj = TenantPolicyManager.objects.get(id=policy_id, tenant_id=tenant_id)
        result['editor_info'] = Cognito.get_cognito_user_by_user_id(str(tenant_policy_obj.editor))
        result['approver_info'] = Cognito.get_cognito_user_by_user_id(str(tenant_policy_obj.approver))
        result['reviewer_info'] = Cognito.get_cognito_user_by_user_id(str(tenant_policy_obj.reviewer))
        query = Q(id=tenant_id)
        t_global_var_data = TenantGlobalVariableData.get_tenant_global_varialbles(query)
        result["global_variables"] = t_global_var_data.get("result") if t_global_var_data else {}
        # Get CustomTags and attach to policy details: pending
        # GET Comments :pending
        # GET tenant global variables and send
        # if editor|review| approver get those user details and attach to policy details
        if not tenant_policy_obj.policy_reference:
            parent_policy_obj = PolicyMaster.objects.get(id=tenant_policy_obj.parent_policy_id)
            parent_policy_url = parent_policy_obj.policy_reference
            # STEP 1: Read content from S3
            # STEP 2: Upload to S3 with new url and url is s3_host+bucket_name+ tenant_id + file_name
            # STEP 3: Save the URL to tenant policy
        # HERE send policy details


class ControlHandlerData(BaseConstant):
    @staticmethod
    def get_control_master_data():
        all_controls = ControlMaster.objects.all().values()
        return all_controls

    @staticmethod
    def save_controls_data(data):
        control_master_obj = ControlMaster(control_name=data.get("control_name"), control_type=data.get("control_type"),
                                            description=data.get("description"), is_deleted=False, is_active=True,
                                           created_by=data.get("created_by"))
        control_master_obj.save()
        return control_master_obj


class HirerecyMapperData(BaseConstant):

    @staticmethod
    def save_hirerey_mapper_data(hirerecy_data):
        hirerecy_master_obj = HirerecyMapper(f_id=hirerecy_data.get("f_id"), c_id=hirerecy_data.get("c_id"))
        return True