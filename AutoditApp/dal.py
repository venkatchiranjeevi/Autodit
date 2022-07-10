from collections import defaultdict

from AutoditApp.models import TenantDepartment as Departments, Roles, TenantGlobalVariables, Tenant, GlobalVariables, \
    RolePolicies, AccessPolicy, TenantFrameworkMaster, TenantPolicyManager, \
    PolicyMaster, ControlMaster, TenantControlMaster, TenantControlAudit, TenantPolicyDepartments, \
    TenantControlsCustomTags, TenantPolicyLifeCycleUsers, TenantPolicyTasks, HirerecyMapper, TenantPolicyVersionHistory
from django.db.models import Q
from .constants import DEFAULT_VIEWS, EDITIOR_VIEWS, ACTIONS_DATA
from .core import fetch_data_from_sql_query
from datetime import datetime, timedelta
from .policy_life_cycle_handler import PolicyLifeCycleHandler, MetaDataDetails


class BaseConstant:
    def __init__(self):
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
        for each_role in data:
            role_obj = Roles(role_name=each_role.get("role_name"), code=each_role.get("role_code"),
                             tenant_id=each_role.get("tenant_id"))
            role_obj.save()
        # Roles.objects.bulk_create(roles_instances)
        return True

    @staticmethod
    def save_single_role(data):
        department_id = data.get("departments", [])
        role_obj = Roles(role_name=data.get("role_name"),
                         code=data.get("role_code"),
                         tenant_id=data.get("tenant_id"),
                         role_type=data.get('role_type'),
                         department_id=department_id[0] if department_id else None)
        role_obj.save()

        actions = ACTIONS_DATA[data.get('role_for')]

        access_policy = AccessPolicy.objects.create(policyname=data.get("policy_name"),
                                                    policy={"views": DEFAULT_VIEWS if data.get(
                                                        'role_for') != 'Editor' else EDITIOR_VIEWS,
                                                            'actionPermissions': actions,
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
                                                     'ceo_email': '', 'cto_name': '', 'cto_email': '', 'logo_url': '',
                                                     'primary_email': '',
                                                     'primary_name': ""},
                                             tenant_id=tenant_obj.id)
        return tenant_obj


class DeparmentsData(BaseConstant):

    @staticmethod
    def get_department_data(tenant_id, department_ids=[]):
        query = Q(tenant_id=tenant_id)
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
    def get_global_variables(teant_id):
        return list(GlobalVariables.objects.all().values())


class TenantGlobalVariableData(BaseConstant):

    @staticmethod
    def get_tenant_global_varialbles(tenant_id):
        t_global_var_data = TenantGlobalVariables.objects.get(tenant_id=tenant_id).result
        try:
            return eval(t_global_var_data)
        except:
            return {}

    @staticmethod
    def save_tenant_global_varialble(data):
        tbv_obj, created = TenantGlobalVariables.objects.get_or_create(tenant_id=data.get("tenant_id"))
        tbv_obj.result = data.get("globalVarialbes", '{}')
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


class TenantFrameworkData(BaseConstant):

    @staticmethod
    def in_active_tenant_framework_data(tenant_id, tenant_master_ids, new_teanant_framworks):
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
    def get_tenant_selected_controls(tenant_id, framework_id):
        query = "select  Id as tenantControlid, TenantFrameworkId, Master_Control_Id as ControlId," \
                " ControlName, Description, Category, ControlCode from TenantControlMaster tcm where TenantFrameworkId in" \
                " (select id from TenantFrameworkMaster tfm where MasterFid = {master_f_id}) and tenantId = {t_id}" \
                " and IsActive = 1"
        tenant_controls_query = query.format(master_f_id=framework_id,
                                             t_id=int(tenant_id))
        tenant_controls = fetch_data_from_sql_query(tenant_controls_query)
        selected_controls_formatted_data = {}
        tenant_framework_id = []
        for tenant_control in tenant_controls:
            tenant_framework_id.append(tenant_control.get('TenantFrameworkId'))
            selected_controls_formatted_data[tenant_control['ControlId']] = tenant_control
        return selected_controls_formatted_data, tenant_framework_id[0] if tenant_framework_id else -99999

    @staticmethod
    def get_all_tenant_controls(tenant_id):
        query = "select  Id as tenantControlid, TenantFrameworkId, Master_Control_Id as ControlId," \
                " ControlName, Description, Category, ControlCode, masterFrameworkId from TenantControlMaster tcm where TenantFrameworkId in" \
                " (select id from TenantFrameworkMaster tfm where tenantId = {t_id}" \
                " and IsActive = 1)"
        tenant_controls_query = query.format(t_id=int(tenant_id))
        tenant_controls = fetch_data_from_sql_query(tenant_controls_query)
        selected_controls_formatted_data = {}
        tenant_framework_id = []
        for tenant_control in tenant_controls:
            tenant_framework_id.append(tenant_control.get('masterFrameworkId'))
            selected_controls_formatted_data[tenant_control['ControlId']] = tenant_control
        return selected_controls_formatted_data, list(set(tenant_framework_id))

    @staticmethod
    def get_policy_counts(tenant_framework_id, tenant_id):
        # TODO need to change this
        query = "SELECT tenantControlId, tenantFrameworkId, COUNT(TenantPolicyId) as con FROM TenantHierarchyMapping where" \
                " tenantFrameworkId= {f_id} and tenantId = {t_id} GROUP BY tenantControlId, tenantFrameworkId"
        query = query.format(f_id=int(tenant_framework_id),
                             t_id=int(tenant_id))
        tenant_hir_details = fetch_data_from_sql_query(query)
        policy_counts = {}
        for h_det in tenant_hir_details:
            policy_counts[h_det['tenantControlId']] = h_det.get('con', 0)
        return policy_counts


class TennatControlHelpers(BaseConstant):

    @staticmethod
    def control_update_handler(tenant_id, data, user_id, user_email):
        control_details = data.get('controlDetails', [])
        master_framework_id = data.get('frameworkId')
        selected_control_ids = [entry.get('controlId') for entry in control_details]
        tenant_controls = TenantControlMaster.objects.filter(tenant_id=int(tenant_id)).filter(
            master_framework_id=int(master_framework_id)).values()
        framework_details = TenantFrameworkMaster.objects.filter(tenant_id=int(tenant_id)).filter(
            master_framework_id=master_framework_id)
        framework_details = framework_details[0]
        active_controls = {}
        inactive_controls = {}
        all_controls = {}
        for control in tenant_controls:
            all_controls[control.get('master_control_id')] = control
            if control.get('is_active'):
                active_controls[control.get('master_control_id')] = control
            else:
                inactive_controls[control.get('master_control_id')] = control

        new_master_controls = list(set(selected_control_ids) - set(list(all_controls.keys())))
        controls_to_inactive = list(set(list(active_controls.keys())) - set(selected_control_ids))
        controls_to_active_ids = list(set(inactive_controls.keys()).intersection(set(selected_control_ids)))
        if not new_master_controls and not controls_to_inactive and not controls_to_active_ids:
            return True
        if controls_to_inactive:
            q1 = Q(tenant_id=int(tenant_id))
            q2 = Q(master_framework_id=int(master_framework_id))
            q3 = Q(master_control_id__in=controls_to_inactive)
            TenantControlMaster.objects.filter(q1 & q2 & q3).update(is_active=0)
        if controls_to_active_ids:
            q1 = Q(tenant_id=int(tenant_id))
            q2 = Q(master_framework_id=int(master_framework_id))
            q3 = Q(master_control_id__in=controls_to_active_ids)
            TenantControlMaster.objects.filter(q1 & q2 & q3).update(is_active=1)
        if new_master_controls:
            control_details = ControlMaster.objects.filter(id__in=new_master_controls).values()
            fcd = {cont.get('id'): cont for cont in control_details}
            need_insertion = []
            for control in new_master_controls:
                master_control = fcd.get(control)
                need_insertion.append(TenantControlMaster(tenant_id=tenant_id,
                                                          tenant_framework_id=framework_details.id,
                                                          master_control_id=control,
                                                          control_name=master_control.get('control_name'),
                                                          control_description=master_control.get('description'),
                                                          created_by=user_email,
                                                          master_framework_id=master_framework_id))
            TenantControlMaster.objects.bulk_create(need_insertion)

        q1 = Q(tenant_id=int(tenant_id))
        q2 = Q(master_framework_id=master_framework_id)
        q3 = Q(is_active=1)
        selected_framework_controls = TenantControlMaster.objects.filter(q1 & q2 & q3).values('master_control_id',
                                                                                              'master_framework_id',
                                                                                              'tenant_framework_id',
                                                                                              'id')

        TennatControlHelpers.policy_handler_on_control_selection(tenant_id,
                                                                 master_framework_id,
                                                                 selected_framework_controls,
                                                                 user_id,
                                                                 user_email)

    @staticmethod
    def policy_handler_on_control_selection(tenant_id,
                                            master_framework_id,
                                            selected_framework_controls,
                                            user_id,
                                            user_email):
        # TODO create TenantHirarect mapper
        selcted_control = [con.get('master_control_id') for con in selected_framework_controls]
        master_selected_polices = HirerecyMapper.objects.filter(f_id=master_framework_id,
                                                                c_id__in=selcted_control).values('policy_id').distinct()
        formatted_master_selected_policies = {sp.get('policy_id'): sp for sp in master_selected_polices}
        exiting_policies = TenantPolicyManager.objects.filter(tenant_id=tenant_id,
                                                              master_framework_id=master_framework_id).values()
        active_policies = {}
        inactive_polices = {}
        existing_all_policies = {}
        for pol in exiting_policies:
            existing_all_policies[pol.get('parent_policy_id')] = pol
            if pol.get('is_active'):
                active_policies[pol.get('parent_policy_id')] = pol
            else:
                inactive_polices[pol.get('parent_policy_id')] = pol

        new_master_policy_ids = list(
            set(formatted_master_selected_policies.keys()) - set(list(existing_all_policies.keys())))
        inactive_policy_ids = list(set(list(existing_all_policies.keys())) - set(formatted_master_selected_policies))
        policies_to_active_ids = list(
            set(inactive_polices.keys()).intersection(set(formatted_master_selected_policies)))
        if inactive_policy_ids:
            q1 = Q(tenant_id=int(tenant_id))
            q2 = Q(master_framework_id=int(master_framework_id))
            q3 = Q(parent_policy_id__in=inactive_policy_ids)
            TenantPolicyManager.objects.filter(q1 & q2 & q3).update(is_active=0)
        if policies_to_active_ids:
            q1 = Q(tenant_id=int(tenant_id))
            q2 = Q(master_framework_id=int(master_framework_id))
            q3 = Q(parent_policy_id__in=policies_to_active_ids)
            TenantPolicyManager.objects.filter(q1 & q2 & q3).update(is_active=1)
        if new_master_policy_ids:
            policy_details = PolicyMaster.objects.filter(id__in=new_master_policy_ids).values()
            fcd = {cont.get('id'): cont for cont in policy_details}
            need_insertion = []
            for pol in new_master_policy_ids:
                master_policy = fcd.get(pol)
                try:
                    need_insertion.append(TenantPolicyManager(tenant_id=tenant_id,
                                                              tenant_policy_name=master_policy.get('policy_name'),
                                                              category=master_policy.get('category'),
                                                              summery=master_policy.get('policy_summery'),
                                                              created_by=user_email,
                                                              version='1',
                                                              status=1,
                                                              is_active=1,
                                                              user_id=user_id,
                                                              parent_policy_id=master_policy.get('id'),
                                                              code=master_policy.get('policy_code'),
                                                              master_framework_id=master_framework_id))
                except Exception as e:
                    pass
            TenantPolicyManager.objects.bulk_create(need_insertion)


class ControlManagementDetailData(BaseConstant):

    @staticmethod
    def get_policies_by_tenant_framework_id_and_tenant_control_id(tenant_f_id, tenant_c_id, tenant_id):
        query = "select tenantPolicyName from TenantPolicyManager tpm  where ParentPolicyID in " \
                "(select PolicyId from HirerecyMapper hm where Fid ={f_id} and Cid ={c_id}) and tenant_id = {t_id}"

        query = query.format(f_id=tenant_f_id, c_id=tenant_c_id, t_id=tenant_id)
        tenant_policies = fetch_data_from_sql_query(query)
        tenant_pol = [pol.get('tenantPolicyName') for pol in tenant_policies]
        return tenant_pol

    @staticmethod
    def get_control_history(tenant_id, control_id):
        history = TenantControlAudit.objects.filter(tenant_id=tenant_id, tenant_control_id=control_id).values("version",
                                                                                                              "created_by",
                                                                                                              "old_control_name",
                                                                                                              "new_control_name",
                                                                                                              "old_control_description",
                                                                                                              "new_control_description",
                                                                                                              "created_on"). \
            order_by('-created_on')
        return history

    @staticmethod
    def save_control_description(data):
        tenant_control_object = TenantControlMaster.objects.get(id=data.get("id"))
        old_description = tenant_control_object.control_description
        old_name = tenant_control_object.control_name
        new_description = data.get("description")
        new_control_name = data.get("control_name")
        tenant_control_object.control_description = new_description
        tenant_control_object.control_name = new_control_name
        tenant_control_object.save()

        last_audit = TenantControlAudit.objects.filter(tenant_control_id=data.get("id")).last()
        if last_audit:
            version = last_audit.version
            version = int(version) + 1
        else:
            version = 1
        tenant_audit = TenantControlAudit(tenant_control_id=data.get("id"), old_control_description=old_description,
                                          new_control_description=new_description,
                                          tenant_framework_id=tenant_control_object.tenant_framework_id,
                                          version=version,
                                          old_control_name=old_name, new_control_name=new_control_name,
                                          tenant_id=data.get("tenant_id"),
                                          created_by=data.get("created_by"))
        tenant_audit.save()

        return tenant_control_object


class PolicyDepartmentsHandlerData(BaseConstant):

    @staticmethod
    def get_departments_by_policy_id(tenant_id, policy_id):
        departments = list(
            TenantPolicyDepartments.objects.filter(tenant_id=tenant_id,
                                                   tenant_policy_id=policy_id).values("id", "department_name"))
        return departments

    @staticmethod
    def save_policy_department_details(data):
        departments_list = data.get("departmentDetails")
        policy_instancess = []
        for each_department in departments_list:
            tpd_obj, created = TenantPolicyDepartments.objects.get_or_create(tenant_id=data.get("tenant_id"),
                                                                             tenant_policy_id=data.get("policyId"),
                                                                             tenant_dep_id=each_department.get("id"),
                                                                             created_by=data.get("created_by"))
            tpd_obj.department_name = each_department.get("name")
            tpd_obj.save()
            policy_instancess.append(tpd_obj)

        deparment_details = TenantPolicyDepartments.objects.filter(tenant_id=data.get("tenant_id"),
                                                                   tenant_policy_id=data.get("policyId")).values("id",
                                                                                                                 "department_name")
        details = [{'id': each_department.get("id"), 'name': each_department.get("department_name")} for each_department
                   in deparment_details]
        return details

    @staticmethod
    def delete_policy_department(policy_department_id, tenant_id, policy_id):
        tpd_obj = TenantPolicyDepartments.objects.get(id=policy_department_id)
        tpd_obj.delete()
        deparment_details = TenantPolicyDepartments.objects.filter(tenant_id=tenant_id,
                                                                   tenant_policy_id=policy_id).values("id",
                                                                                                      "department_name")
        details = [{'id': each_department.get("id"), 'name': each_department.get("department_name")} for each_department
                   in deparment_details]
        return details


class TenantPolicyCustomTagsData(BaseConstant):
    @staticmethod
    def get_policy_custom_tags(tenant_id, policy_id):
        custom_tags = TenantControlsCustomTags.objects.filter(tenant_id=tenant_id, tenant_policy_id=policy_id).values(
            "id",
            "tag_name",
            "tag_description")
        return custom_tags

    @staticmethod
    def save_custom_tags(data):
        custom_tags = data.get("tagsDetails")
        custom_tags_instancess = [TenantControlsCustomTags(tenant_id=data.get("tenant_id"),
                                                           tenant_policy_id=data.get("policyId"),
                                                           tag_name=each_tag.get("tagName"),
                                                           tag_description='',
                                                           is_active=1) for each_tag in
                                  custom_tags]

        TenantControlsCustomTags.objects.bulk_create(custom_tags_instancess)
        tags = TenantPolicyCustomTagsData.get_policy_tags(data.get("policyId"), data.get("tenant_id"))
        return tags

    @staticmethod
    def delete_policy_custom_tag(tag_id, tenant_id, policy_id):
        tcc_obj = TenantControlsCustomTags.objects.get(id=tag_id)
        tcc_obj.delete()
        tags = TenantPolicyCustomTagsData.get_policy_tags(policy_id, tenant_id)
        return tags

    @staticmethod
    def get_policy_tags(policy_id, tenant_id):
        details = TenantControlsCustomTags.objects.filter(tenant_id=tenant_id).filter(tenant_policy_id=policy_id)
        details = details.values('tag_name', 'id')
        return [{'tagId': det['id'], 'tagName': det['tag_name']} for det in details]


class TenantPolicyLifeCycleUsersData(BaseConstant):

    @staticmethod
    def get_assigned_users_by_policy_id(tenant_id, policy_id):
        owners = TenantPolicyLifeCycleUsers.objects.filter(tenant_id=tenant_id, policy_id=policy_id,
                                                           is_active=True).values("id",
                                                                                  "owner_type",
                                                                                  "owner_name",
                                                                                  "owner_user_id", "owner_email")
        owners = [{"ownerId": owner.get("id"),
                   "owner_type": owner.get("owner_type"),
                   "owner_name": owner.get("owner_name"),
                   "user_id": owner.get("owner_user_id"),
                   "owner_email": owner.get("owner_email"),
                   "owner_code": owner.get("owner_name")[:2]}
                  for owner in owners]
        return owners

    @staticmethod
    def save_policy_assigned_users(data):
        # FETCH policy present state
        # Meta data get details based on policy state and get accessUser
        # Fetch user roles and fetch user type
        # if MetaData(PolictpresentState) in role_types:
        #   CREATE USER TASK
        #   check if same state has one or multiple department tasks
        #   1)For same state check any department task
        #   if dapartment task then convert department into user task
        #   else
        # Create user task

        # Tasks --> TenantPolicyTasks
        # Meta Data --> MetaData
        policy_id = data.get("policyId")
        tenant_id = data.get("tenant_id")
        policy_life_obj = PolicyLifeCycleHandler.get_policy_details_by_policy_id(policy_id)
        policy_state = policy_life_obj.state
        policy_meta_data = MetaDataDetails.get_policy_access_users(policy_state)
        state_users = policy_meta_data[0].get("state_user")
        access_user = policy_meta_data[0].get("access_user")
        task_verify = policy_meta_data[0].get("task_verify")
        assignee_type = data.get("type")
        if assignee_type == 'assignee':
            # TODO will remove once complete integration is done
            assignee_type = 'editor'

        users = data.get("userDetails")
        for each_user in users:
            # TODO If any pending task for this department is avaialbe then need to assign task for user
            user_id = each_user.get("userId")

            # user_details = Cognito.get_cognito_user_by_user_id(user_id)
            # user_role_ids = eval(user_details.get('custom:role_id', "[]"))
            # role_types = Roles.objects.filter(role_id__in=user_role_ids).values('role_type')
            # role_types = [each_role_type.get("role_type") for each_role_type in role_types]
            if access_user == assignee_type:
                query = (Q(user_email__isnull=True) | Q(user_email=""))
                query &= Q(tenant_id=tenant_id, policy_id=policy_id, policy_state=policy_meta_data[0].get("key"))
                TenantPolicyTasks.objects.filter(query).update(task_status=2)
                TenantPolicyTasks.objects.create(tenant_id=tenant_id,
                                                 policy_id=policy_id,
                                                 task_status=0,
                                                 user_email=each_user.get("ownerEmail"),
                                                 user_id=each_user.get("userId"),
                                                 task_type=task_verify,
                                                 allowed_roles=state_users,
                                                 task_name=policy_meta_data[0].get("state_display_name"),
                                                 policy_state=policy_meta_data[0].get("key"),
                                                 department_id=0)

            tlc_obj, created = TenantPolicyLifeCycleUsers.objects.get_or_create(tenant_id=tenant_id,
                                                                                policy_id=policy_id,
                                                                                owner_type=assignee_type,
                                                                                owner_user_id=user_id,
                                                                                is_active=True)
            if created:
                tlc_obj.owner_name = each_user.get("ownerName")
                tlc_obj.owner_email = each_user.get("ownerEmail")
                tlc_obj.owner_code = each_user.get("ownerCode")
                tlc_obj.save()
        assignee_users = TenantPolicyLifeCycleUsers.objects.filter(tenant_id=tenant_id,
                                                                   policy_id=policy_id,
                                                                   owner_type=assignee_type,
                                                                   is_active=True). \
            values("id", "owner_type", "owner_name", "owner_user_id", "owner_code")
        return assignee_users

    @staticmethod
    def delete_assignee_user_by_assignee_id(assignee_id, policy_id, assignee_type, tenant_id):
        if assignee_type == 'assignee':
            assignee_type = 'editor'
        tplc_obj = TenantPolicyLifeCycleUsers.objects.get(id=assignee_id)
        tplc_obj.is_active = False
        tplc_obj.in_active_date = datetime.now()
        tplc_obj.save()
        assignee_users = TenantPolicyLifeCycleUsers.objects.filter(tenant_id=tenant_id,
                                                                   policy_id=policy_id,
                                                                   owner_type=assignee_type,
                                                                   is_active=True). \
            values("id", "owner_type", "owner_name", "owner_user_id", "owner_code")
        # TODO If any pending task is der then either make it department task or another task
        return assignee_users


class DashBoardData(BaseConstant):

    @staticmethod
    def get_dashboard_controls_details(tenant_id, master_f_id):
        result = {}
        selected_controls, tenant_framework_id = TenantFrameworkData.get_tenant_selected_controls(tenant_id,
                                                                                                  master_f_id)
        hirarecy_objects = HirerecyMapper.objects.filter(f_id=master_f_id, c_id__in=list(selected_controls.keys()))
        policy_ids = []
        mapper = defaultdict(list)
        for hir in hirarecy_objects:
            policy_ids.append(hir.policy_id)
            mapper[hir.c_id].append(hir.policy_id)
        policy_ids = list(set(policy_ids))

        policy_details = TenantPolicyManager.objects.filter(tenant_id=tenant_id, parent_policy_id__in=policy_ids).values()
        policy_mapper = {pol.get('id'): pol for pol in policy_details}
        all_controls = ControlMaster.objects.filter(framework_id=int(master_f_id), id__in=list(mapper.keys())).values(
            'id',
            'control_name',
            'control_code',
            'category')
        selected_control_ids = selected_controls.keys()
        control_details_list = []
        completed_controls = 0
        for control in all_controls:
            opted = False
            control_details = {'master_control_id': control.get('id'), 'control_name': control.get('control_name'),
                               'control_code': control.get('control_code'), 'policies_count': 0}
            if control.get('id') in selected_control_ids:
                selected_con = selected_controls[control.get('id')]
                control_details['control_name'] = selected_con.get('ControlName')
                control_details['control_code'] = selected_con.get('ControlCode')
                control_policies = mapper.get(control.get('id'), [])
                control_policies = list(set(control_policies))
                completed = True
                for po in control_policies:
                    if policy_mapper.get(po, {}).get('state') != 'PUB':
                        completed = False
                        break
                if completed:
                    completed_controls += 1
                control_details['policies_count'] = len(control_policies)

                opted = True
            control_details['is_control_selected'] = opted
            control_details_list.append(control_details)
        result['controls'] = control_details_list
        result['totalControls'] = len(selected_controls)
        result['closedControls'] = completed_controls
        result['pendingControls'] = len(selected_controls) - completed_controls
        return result

    @staticmethod
    def get_policies_details(tenant_id, master_f_id, user):
        department_ids = user.departments
        isAdmin = user.isAdmin

        if isAdmin:
            selected_policies = TenantPolicyManager.objects.filter(tenant_id=tenant_id, is_active=True,
                                                                   master_framework_id=master_f_id).values()
        else:
            selected_policies = fetch_data_from_sql_query(
                'select a.tenantPolicyName as tenant_policy_name, a.code as policy_code, a.id, a.category, a.State as state'
                ' from TenantPolicyManager a'
                ' where a.tenant_id={} and a.isActive=1'
                ' and a.MasterFrameworkId={} and (a.id in (Select policyId from TenantPolicyLifeCycleUsers where ownerUserId = "{}") or'
                '(a.id in (Select TenantPolicyId from TenantPolicyDepartments tpd where tenant_id = {} and TenantDepartment_id in {})))'
                    .format(tenant_id, master_f_id, user.userid, tenant_id,
                            "({})".format(','.join(str(x) for x in department_ids))))

        approved_count = 0
        final_details = {}
        policy_dets = []
        formatted_policies = {}
        for each_policy in selected_policies:
            formatted_policies[each_policy.get('id')] = each_policy
            details = {'policyName': each_policy.get('tenant_policy_name'), 'category': each_policy.get('category'),
                       'policyId': each_policy.get('id'), 'policyCode': each_policy.get('policy_code'),
                       'policyState': each_policy.get('state')}
            if each_policy.get('state') == 'PUB':
                approved_count += 1
                details['isPolicyApproved'] = True
            details['isPolicySelected'] = True
            policy_dets.append(details)
        final_details['policies'] = policy_dets
        final_details['totalPolicies'] = len(policy_dets)
        final_details['approvedPolicies'] = approved_count
        final_details['pendingPolicies'] = final_details['totalPolicies'] - final_details['approvedPolicies']
        return final_details, formatted_policies

    @staticmethod
    def get_recent_activities(tenant_id, master_f_id, user, policy_details, pending_tasks):

        present_date = datetime.now()
        start_date = datetime.now() - timedelta(days=10)
        start_date = start_date.replace(minute=0, hour=0, second=0)
        end_date = present_date
        policy_id_objects = TenantPolicyManager.objects.filter(master_framework_id=master_f_id).values('id')
        # departments
        policy_ids = []
        parent_policy_ids = []
        for pol in policy_id_objects:
            policy_ids.append(pol.get('id'))
            parent_policy_ids.append(pol.get('parent_policy_id'))
        if not policy_ids:
            return []
        policy_ids = [pol.get('id') for pol in policy_id_objects]
        role_details = eval(user.role_id)
        role_details = Roles.objects.filter(role_id__in=role_details).values('role_type', 'department_id')
        role_types = []
        department_ids = []
        for role in role_details:
            department_ids.append(role.get('department_id'))
            role_types.append(role.get('role_type'))
        query = "SELECT tcm.tenantId, hm.Cid, tpm.id as PolicyId, tcm.ControlName," \
                " tcm.Description, hm.Fid from TenantControlMaster tcm Inner join HirerecyMapper hm" \
                " on tcm.Master_Control_Id = hm.Cid and hm.Fid = tcm.masterFrameworkId  Inner Join " \
                "TenantPolicyManager tpm  on tpm.ParentPolicyID = hm.PolicyId where " \
                "hm.Fid = {f_id} and hm.PolicyId  in {policy_ids} and tcm.tenantId  = {tennant_id}" \
                " and tcm.IsActive = 1 order by hm.id"
        if len(policy_ids) == 1:
            policy_ids += 1
        query = query.format(f_id=master_f_id,
                             policy_ids=str(tuple(policy_ids)),
                             tennant_id=tenant_id)
        control_details = fetch_data_from_sql_query(query)
        policy_controls = defaultdict(list)
        for con in control_details:
            policy_controls[con.get('PolicyId')].append(con.get('ControlName'))
        policy_departments =TenantPolicyDepartments.objects.filter(tenant_policy_id__in=policy_ids)
        policy_department_formatted = defaultdict(list)
        for po_depar in policy_departments:
            policy_department_formatted[po_depar.tenant_policy_id].append(po_depar.department_name)

        department_tasks = []
        query = Q(tenant_id=tenant_id) & Q(policy_id__in=policy_ids)
        query = query & ~Q(task_status=0)
        query = query & Q(created_on__range=(start_date, end_date))
        if user.isAdmin:
            tasks = TenantPolicyTasks.objects.filter(query).values()
        else:
            user_query = query & Q(user_email=user.email)
            tasks = TenantPolicyTasks.objects.filter(user_query).values()
            depart_query = query & Q(department_id__in=department_ids)
            department_tasks = TenantPolicyTasks.objects.filter(depart_query).values()
        details = []
        status = {0: 'Pending', 1: 'Completed', 2: 'Rejected'}
        for task in tasks:
            policy_det = policy_details.get(task.get('policy_id'), {})
            con_policy = policy_controls.get(task.get('policy_id'), [])
            if not policy_det:
                continue
            det = {'policyName': policy_det.get('tenant_policy_name'),
                   'policyId': task.get('policy_id'),
                   'taskName': task.get('task_name'),
                   'taskAssignee': task.get('user_email'),
                   'taskType': 'userTask',
                   'departments': policy_department_formatted.get(task.get('policy_id'), []),
                   'version': policy_det.get('version'),
                   'taskStatus': status.get(task.get('task_status')),
                   'createdOn': task.get('created_on'),
                   'policyState': task.get('policy_state'),
                   'taskPerformedBy': task.get('task_performed_by'),
                   'noofControlsEffected': len(con_policy),
                   'controlDetails': con_policy,
                    'lastUpdatedOn': task.get('action_date'),
                   'lastUpdatedBy':  task.get('action_performed_by')}
            details.append(det)

        for task in department_tasks:
            policy_det = policy_details.get(task.get('policy_id'), {})
            if not policy_det:
                continue
            con_policy = policy_controls.get(task.get('policy_id'), [])
            det = {'policyName': policy_det.get('tenant_policy_name'),
                   'policyId': task.get('policy_id'),
                   'taskName': task.get('task_name'),
                   'taskAssignee': task.get('user_email'),
                   'version': policy_det.get('version'),
                   'taskStatus': status.get(task.get('task_status')),
                   'departments': policy_department_formatted.get(task.get('policy_id'),[]),
                   'createdOn': task.get('created_on'),
                   'taskType': 'departmentTask',
                   'policyState': task.get('policy_state'),
                   'noofControlsEffected': len(con_policy),
                   'controlDetails': con_policy,
                   'lastUpdatedOn': task.get('action_date'),
                   'lastUpdatedBy': task.get('action_performed_by')}
            details.append(det)

        version_query = Q(action_date__range=(start_date, end_date))
        version_query = version_query & Q(policy_id__in=policy_ids)
        if user.isAdmin:
            tasks = TenantPolicyVersionHistory.objects.filter(version_query).values()
        else:
            user_query = version_query & Q(action_performed_by=user.email)
            tasks = TenantPolicyVersionHistory.objects.filter(user_query).values()
        for task in tasks:
            policy_det = policy_details.get(task.get('policy_id'), {})
            if not policy_det:
                continue
            con_policy = policy_controls.get(task.get('policy_id'), [])
            det = {'policyName': policy_det.get('tenant_policy_name'),
                   'policyId': task.get('policy_id'),
                   'taskName': task.get('action_performed'),
                   'version': policy_det.get('version'),
                   'taskAssignee': task.get('action_performed_by'),
                   'taskStatus': status.get(task.get('version_type')),
                   'departments': policy_department_formatted.get(task.get('policy_id'), []),
                   'createdOn': task.get('created_on'),
                   'taskType': 'policyOperations',
                   'policyState': task.get('status'),
                   'noofControlsEffected': len(con_policy),
                   'controlDetails': con_policy,
                   'lastUpdatedOn': task.get('action_date'),
                   'lastUpdatedBy':  task.get('action_performed_by')}
            details.append(det)

        # need to get policy controls, departments, version
        all_tasks = details[:10]
        return all_tasks

    @staticmethod
    def pending_tasks(tenant_id, master_f_id, user, policy_details):
        # TODO need to take department tasks also
        policy_id_objects = TenantPolicyManager.objects.filter(master_framework_id=master_f_id).values('id')
        policy_ids = [pol.get('id') for pol in policy_id_objects]
        role_details = eval(user.role_id)
        role_details = Roles.objects.filter(role_id__in=role_details).values('role_type', 'department_id')
        role_types = []
        department_ids = []
        for role in role_details:
            department_ids.append(role.get('department_id'))
            role_types.append(role.get('role_type'))
        department_tasks = []
        if user.isAdmin:
            tasks = TenantPolicyTasks.objects.filter(tenant_id=tenant_id, policy_id__in=policy_ids,
                                                     task_status=0).values()
        else:
            tasks = TenantPolicyTasks.objects.filter(tenant_id=tenant_id, user_email=user.email,
                                                     policy_id__in=policy_ids,
                                                     task_status=0).values()
            department_tasks = TenantPolicyTasks.objects.filter(tenant_id=tenant_id, policy_id__in=policy_ids,
                                                                department_id__in=department_ids,
                                                                task_status=0).values()
        details = []
        status = {0: 'Pending', 1: 'Completed', 2: 'Rejected'}
        for task in tasks:
            policy_det = policy_details.get(task.get('policy_id'), {})
            det = {'policyName': policy_det.get('tenant_policy_name'),
                   'taskName': task.get('task_name'),
                   'taskAssignee': task.get('user_email'),
                   'taskType': 'userTask',
                   'taskStatus': status.get(task.get('task_status')),
                   'createdOn': task.get('created_on'),
                   'policyState': task.get('policy_state'),
                   'taskPerformedBy': task.get('task_performed_by'),
                   'taskPerformedOn': task.get('task_performed_on')}
            details.append(det)

        for task in department_tasks:
            policy_det = policy_details.get(task.get('policy_id'), {})
            det = {'policyName': policy_det.get('tenant_policy_name'),
                   'taskName': task.get('task_name'),
                   'taskAssignee': task.get('user_email'),
                   'taskStatus': status.get(task.get('task_status')),
                   'createdOn': task.get('created_on'),
                   'taskType': 'departmentTask',
                   'policyState': task.get('policy_state'),
                   'taskPerformedBy': task.get('task_performed_by'),
                   'taskPerformedOn': task.get('task_performed_on')}
            details.append(det)
        return details
        # if 'ADMIN' in role_types:9
        #     return {}
        # return {}

    @staticmethod
    def get_dashboard_data(tenant_id, framework_id, user):
        # STEP1: Get policy details
        data = {}
        data['policyDetails'], formatted_policies = DashBoardData.get_policies_details(tenant_id, framework_id, user)
        data['pendingTasks'] = DashBoardData.pending_tasks(tenant_id, framework_id, user, formatted_policies)
        data['recentActivities'] = DashBoardData.get_recent_activities(tenant_id, framework_id, user, formatted_policies, data['pendingTasks'])
        data['controlDetails'] = DashBoardData.get_dashboard_controls_details(tenant_id, framework_id)

        return data
