from AutoditApp.models import TenantDepartment as Departments, Roles, TenantGlobalVariables, Tenant, GlobalVariables, \
    RolePolicies, AccessPolicy, TenantFrameworkMaster, TenantHierarchyMapping, TenantPolicyManager, \
    PolicyMaster, ControlMaster, TenantControlMaster, TenantControlAudit, TenantPolicyDepartments, TenantControlsCustomTags
from django.db.models import Q
from .constants import DEFAULT_VIEWS, EDITIOR_VIEWS
from AutoditApp.AWSCognito import Cognito
from .core import fetch_data_from_sql_query
from .S3_FileHandler import S3FileHandlerConstant

from .sql_queries import TENANT_CONTROL_ID, CONTROLS_MASTER, TENANT_FRAMEWORK_DETAILS, TENANT_FRAMEWORK_POLICIES, \
    CONTROL_FRAMEWORK_DETAILS
from .sql_queries import TENANT_CONTROL_ID, CONTROLS_MASTER


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
                                                    policy={"views": DEFAULT_VIEWS if data.get(
                                                        'role_for') != 'Editor' else EDITIOR_VIEWS, 'actions': [],
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


class TenantFrameworkData(BaseConstant):

    @staticmethod
    def get_tenant_framework_details(tenant_id, control_id, framework_id):
        query = TENANT_FRAMEWORK_DETAILS.format(control_id, framework_id, tenant_id)
        tenant_controls = fetch_data_from_sql_query(query)
        return tenant_controls

    @staticmethod
    def get_tenant_frameworks(tenant_id, framework_id):
        query = Q(is_active=1, tenant_id=tenant_id)
        if framework_id:
            query &= Q(master_framework_id=framework_id)
        tenant_frameworks = TenantFrameworkMaster.objects.filter(query).values("id", "tenant_framework_name",
                                                                               'master_framework_id', "framework_type")
        return tenant_frameworks

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

    @staticmethod
    def get_tenant_selected_controls(tenant_id, framework_id):
        query = "select  Id as tenantControlid, TenantFrameworkId, Master_Control_Id as ControlId," \
                " ControlName, Description, Category, ControlCode from TenantControlMaster tcm where TenantFrameworkId  in" \
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
    def get_policy_counts(tenant_framework_id, tenant_id):
        query = "SELECT tenantControlId, tenantFrameworkId, COUNT(TenantPolicyId) as con FROM TenantHierarchyMapping where" \
                " tenantFrameworkId= {f_id} and tenantId = {t_id} GROUP BY tenantControlId, tenantFrameworkId"
        query = query.format(f_id=int(tenant_framework_id),
                             t_id=int(tenant_id))
        tenant_hir_details = fetch_data_from_sql_query(query)
        policy_counts = {}
        for h_det in tenant_hir_details:
            policy_counts[h_det['tenantControlId']] = h_det.get('con', 0)
        return policy_counts

    @staticmethod
    def get_control_masters():
        framework_controls = fetch_data_from_sql_query(CONTROLS_MASTER)
        return framework_controls


class TenantControlMasterData(BaseConstant):

    @staticmethod
    def get_tenant_controls_data(tenant_f_ids):
        ids = ",".join([str(t_fid) for t_fid in tenant_f_ids])
        if not ids:
            return []
        query = TENANT_CONTROL_ID.format(ids)
        tenant_controls = fetch_data_from_sql_query(query)
        return tenant_controls

    @staticmethod
    def get_policies_count_by_tenant_id(tenant_id):
        hierarchy_mappings = TenantHierarchyMapping.objects.filter(tenant_id=tenant_id,
                                                                   tenant_framework_id__isnull=False). \
            values("tenant_policy_id", "tenant_framework_id", "tenant_control_id")
        return hierarchy_mappings

    @staticmethod
    def get_policies_by_control_and_framework_id(tenant_framework_id, tenant_control_id, tenant_id):
        TenantHierarchyMapping.objects.filter(tenant_id=tenant_id, tenant_framework_id=tenant_framework_id,
                                              tenant_control_id=tenant_control_id).values("")

    @staticmethod
    def save_tenant_controls(data):
        controls = data.get("controls")
        tenant_id = data.get("tenant_id")
        tenant_framework_id = data.get("tenant_framework_id")
        created_by = data.get("created_by")
        is_selected = data.get("is_selected")
        tcm_obj = None
        if not data.get("is_all_controls"):
            if is_selected:
                tcm_obj = TenantControlMaster.objects.create(tenant_id=tenant_id,
                                                             tenant_framework_id=tenant_framework_id,
                                                             control_name=controls[0].get("control_name"),
                                                             master_control_id=controls[0].get("master_control_id"),
                                                             created_by=data.get("created_by"))

                TenantHierarchyMapping.objects.create(tenant_id=tenant_id, tenant_framework_id=tenant_framework_id,
                                                      tenant_control_id=tcm_obj.id, created_by=created_by,
                                                      controller_id=controls[0].get("master_control_id"))
            else:
                TenantControlMaster.objects.filter(id=controls[0].get("tenant_control_id")).delete()
                TenantHierarchyMapping.objects.filter(tenant_id=tenant_id, tenant_framework_id=tenant_framework_id,
                                                      tenant_control_id=data.get("tenant_control_id")).delete()

        else:
            all_control_master_data = TenantFrameworkData.get_control_masters()
            if is_selected:
                for each_control in all_control_master_data:
                    tcm_object, created = TenantControlMaster.objects.get_create(tenant_id=tenant_id,
                                                                                 tenant_framework_id=tenant_framework_id,
                                                                                 master_control_id=each_control.get(
                                                                                     "c_id"))
                    if created:
                        tcm_object.control_name = each_control.get("ControlName")
                        tcm_object.created_by = data.get("created_by")
                        tcm_object.save()

                    thm_object, created = TenantHierarchyMapping.objects.get_or_create(tenant_id=tenant_id,
                                                                                       tenant_framework_id=tenant_framework_id,
                                                                                       tenant_control_id=tcm_object.id)
            else:
                TenantControlMaster.objects.filter(tenant_framework_id=tenant_framework_id).delete()
                TenantHierarchyMapping.objects.filter(tenant_id=tenant_id,
                                                      tenant_framework_id=tenant_framework_id).delete()

        return tcm_obj


class TennatControlHelpers(BaseConstant):

    @staticmethod
    def control_update_handler(tenant_id, data, user_id):
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
        if controls_to_inactive:
            q1 = Q(tenant_id=int(tenant_id))
            q2 = Q(master_framework_id=int(master_framework_id))
            q3 = Q(master_control_id__in=controls_to_inactive)
            TenantControlMaster.objects.filter(q1 & q2 & q3).update(is_active=0)
        #     TODO play with policies
        if controls_to_active_ids:
            q1 = Q(tenant_id=int(tenant_id))
            q2 = Q(master_framework_id=int(master_framework_id))
            q3 = Q(master_control_id__in=controls_to_active_ids)
            TenantControlMaster.objects.filter(q1 & q2 & q3).update(is_active=1)
        #     TODO play with policies
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
                                                          created_by=user_id,
                                                          master_framework_id=master_framework_id))
            TenantControlMaster.objects.bulk_create(need_insertion)
        # TODO change this to local control ids instead of query. For ease of purpose querying
        if new_master_controls or controls_to_inactive or controls_to_active_ids:
            q1 = Q(tenant_id=int(tenant_id))
            q2 = Q(master_framework_id=master_framework_id)
            q3 = Q(is_active=1)
            # TODO at present going with one policy for one framework
            selected_framework_controls = TenantControlMaster.objects.filter(q1 & q2 & q3).values('master_control_id')
            selected_master_controls = [con['master_control_id'] for con in selected_framework_controls]
            # TennatControlHelpers.policy_handler_on_control_selection(tenant_id,
            #                                                          master_framework_id,
            #                                                          framework_details,
            #                                                          selected_master_controls)

    @staticmethod
    def policy_handler_on_control_selection(tenant_id,
                                            master_framework_id,
                                            tenant_framework_details,
                                            inactivated_controls,
                                            activated_controls,
                                            added_controls):
        if inactivated_controls:
            if len(inactivated_controls) == 1:
                inactivated_controls += 1

        if activated_controls:
            if len(activated_controls) == 1:
                activated_controls += 1

        if added_controls:
            if len(added_controls) == 1:
                added_controls += 1

        polices_query = "select id as policyId, PolicyName, policy_code, Summery from PolicyMaster pm  " \
                        "where id in (select DISTINCT(PolicyId) from HirerecyMapper hm where Fid  = {f_id} and Cid  " \
                        "in {cids}}) "
        if len(selected_controls) == 1:
            selected_controls += 1
        polices_query = polices_query.format(f_id=str(master_framework_id),
                                             cids=str(tuple(selected_controls)))
        policy_details = fetch_data_from_sql_query(polices_query)
        formatted_policy_details = {po.get('policyId'): po for po in policy_details}

    @staticmethod
    def policy_handler_for_new_controls(added_controls, tennant_id, master_framework_id):
        master_polices_query = "select id as policyId, PolicyName, policy_code, Summery from PolicyMaster pm  " \
                               "where id in (select DISTINCT(PolicyId) from HirerecyMapper hm where Fid  = {f_id} and Cid  " \
                               "in {cids}}) "
        master_polices_query = master_polices_query.format(cids=str(tuple(added_controls)),
                                                           f_id=str(master_framework_id))
        master_policies = fetch_data_from_sql_query(master_polices_query)

        existing_policies = ""

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


class ControlManagementDetailData(BaseConstant):

    @staticmethod
    def get_controls_data_by_control_id_framework_id(control_id, framework_id, tenant_id):
        query = CONTROL_FRAMEWORK_DETAILS.format(tenant_id, control_id, framework_id)
        controls_data = fetch_data_from_sql_query(query)
        return controls_data

    @staticmethod
    def get_policies_by_tenant_framework_id_and_tenant_control_id(tenant_f_id, tenant_c_id, tenant_id):
        query = TENANT_FRAMEWORK_POLICIES.format(tenant_f_id, tenant_c_id, tenant_id)
        tenant_policies = fetch_data_from_sql_query(query)
        return tenant_policies

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


class PolicyDetailsData(BaseConstant):
    @staticmethod
    def get_policy_details(policy_id, tenant_id):
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
            source_key = parent_policy_url.split("/") if parent_policy_url else None

            s3_bucket = S3FileHandlerConstant.s3_bucket_object(S3FileHandlerConstant.POLICY_BUCKET_SOURCE)

            copy_source = {
                'Bucket': S3FileHandlerConstant.POLICY_BUCKET_SOURCE,
                'Key': '{}/{}'.format(S3FileHandlerConstant.POLICY_BUCKET_SUB_FOLDER, source_key[-1])
            }
            tenant_policy_name = "{}_{}_{}".format(tenant_id, parent_policy_obj.policy_name, source_key)
            s3_bucket.copy(copy_source,
                           '{}/mani_{}'.format(S3FileHandlerConstant.TENANT_POLICY_BUCKET, tenant_policy_name))
            del source_key[-1]
            final_url = "{}/{}".format(source_key.join(""), tenant_policy_name)
            print(final_url)

            # STEP 1: Read content from S3
            # STEP 2: Upload to S3 with new url and url is s3_host+bucket_name+ tenant_id + file_name
            # STEP 3: Save the URL to tenant policy
        # HERE send policy details


class PolicyDepartmentsHandlerData(BaseConstant):

    @staticmethod
    def get_departments_by_policy_id(tenant_id, policy_id):
        departments = list(TenantPolicyDepartments.objects.filter(tenant_id=tenant_id, tenant_policy_id=policy_id).values("id",
                                                                    "department_name", ))
        return departments


    @staticmethod
    def save_policy_department_details(data):
        departments_list = data.get("departmentDetails")
        policy_instancess = []
        for each_department in departments_list:
            tpd_obj = TenantPolicyDepartments(tenant_id=data.get("tenant_id"),
                                              tenant_policy_id=data.get("policyId"),
                                              department_name=each_department.get("departmentName"),
                                              tenant_dep_id=each_department.get("id"), created_by=data.get("created_by"))
            policy_instancess.append(tpd_obj)

        TenantPolicyDepartments.objects.bulk_create(policy_instancess)
        return True

    @staticmethod
    def delete_policy_department(policy_department_id):
        tpd_obj = TenantPolicyDepartments.objects.get(id=policy_department_id)
        tpd_obj.delete()
        return True


class TenantPolicyCustomTagsData(BaseConstant):
    @staticmethod
    def get_policy_custom_tags(tenant_id, policy_id):
        custom_tags = TenantControlsCustomTags.objects.filter(tenant_id=tenant_id, tenant_policy_id=policy_id).values("id",
                                                                                        "tag_name", "tag_description")
        return custom_tags

    @staticmethod
    def save_custom_tags(data):
        custom_tags = data.get("tagsDetails")
        custom_tags_instancess = []
        for each_tag in custom_tags:
            tcc_obj = TenantControlsCustomTags(tenant_id=data.get("tennat_id"), tenant_policy_id=data.get("policyId"),
                                     tag_name=each_tag.get("tagName"))
            custom_tags_instancess.append(tcc_obj)

        TenantControlsCustomTags.objects.bulk_create(custom_tags_instancess)
        return True

    @staticmethod
    def delete_policy_custom_tag(tag_id):
        tcc_obj = TenantControlsCustomTags.objects.get(id=tag_id)
        tcc_obj.delete()
        return True


