from collections import defaultdict
from datetime import datetime

from django.db.models import Q

from AutoditApp.S3_FileHandler import S3FileHandlerConstant
from AutoditApp.core import fetch_data_from_sql_query
from AutoditApp.models import ControlMaster, FrameworkMaster, HirerecyMapper, MasterPolicyParameter
from AutoditApp.models import PolicyMaster


class BaseConstant:
    def __init__(self):
        pass


class ControlHandlerData(BaseConstant):
    @staticmethod
    def get_control_master_data_by_control_ids(control_ids):
        all_controls = ControlMaster.objects.filter(id__in=control_ids, is_deleted=False, is_active=True). \
            values("id", "control_name", "control_type", "control_code", "description")
        return all_controls

    @staticmethod
    def save_controls_data(data, user_id):
        id = data.get('id')
        control_name = data.get('control_name')
        control_code = data.get('control_code')
        description = data.get('description')
        framework_id = data.get('framework_id')
        if id:
            control_master_obj = ControlMaster.objects.get(id=id)
            control_master_obj.control_name = control_name
            control_master_obj.control_code = control_code
            control_master_obj.description = description
            control_master_obj.framework_id = framework_id
            control_master_obj.created_by = user_id
        else:
            control_master_obj = ControlMaster(control_name=control_name,
                                               description=description,
                                               control_code=control_code,
                                               framework_id=framework_id,
                                               is_deleted=False,
                                               is_active=True,
                                               created_by=user_id)
        control_master_obj.save()
        return control_master_obj


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
    def save_frameworks(data, user_id):
        framework_obj = FrameworkMaster(framework_name=data.get("framework_name"),
                                        framework_type=data.get("framework_type"),
                                        description=data.get("description"),
                                        is_deleted=False,
                                        is_active=True)
        framework_obj.save()
        return framework_obj


class HirerecyMapperData(BaseConstant):

    @staticmethod
    def get_controls_and_policies_by_framework_id(f_id):
        if f_id:
            frameworks_data = ControlMaster.objects.filter(framework_id=f_id)
        else:
            frameworks_data = ControlMaster.objects.all()
        frameworks_data = list(frameworks_data.values("id",
                                                      "framework_id",
                                                      "control_code",
                                                      "control_name",
                                                      "description",
                                                      "is_active",
                                                      "category"))
        return frameworks_data

    @staticmethod
    def get_framework_and_policies_by_policy_id(policies_ids):
        frameworks_data = list(HirerecyMapper.objects.filter(policy_id__in=policies_ids).values("id",
                                                                                                "f_id", "policy_id"))
        return frameworks_data

    @staticmethod
    def get_selected_controls_block_details(policy_id, framework_ids):
        q1 = Q(policy_id=int(policy_id))
        q2 = Q(is_active=1)
        q3 = Q(f_id__in=framework_ids)
        existing_controls = HirerecyMapper.objects.filter(q1 & q2 & q3).values('id',
                                                                               'f_id',
                                                                               'c_id',
                                                                               'policy_id',
                                                                               'is_active')
        formatted_data = defaultdict(list)
        for control in existing_controls:
            formatted_data[control.get('f_id')].append(control.get('c_id'))
        controls_query = "select c.id as Cid, c.ControlName, c.Description as cDes, c.ControlCode as controlCode, fm.id as FrameworkId, fm.FrameworkName, fm.Description as FrameworkDes from ControlMaster c left join FrameworkMaster fm  on c.FrameworkId = fm.Id  where c.FrameworkId in {f_id}"
        if len(framework_ids) == 1:
            framework_ids += framework_ids
        controls_query = controls_query.format(f_id=str(tuple(framework_ids)))
        # if f_id:
        #     controls_query += " where FrameworkId = {f_id}"
        #     controls_query = controls_query.format(f_id=str(f_id))
        framework_controls_data = fetch_data_from_sql_query(controls_query)
        result = {}
        for control_data in framework_controls_data:
            framework_id = control_data['FrameworkId']
            framework_name = control_data['FrameworkName']
            control_id = control_data.get('Cid')
            is_allocated = False
            if control_id in formatted_data.get(framework_id, []):
                is_allocated = True
            control_details = {
                'ControlName': control_data.get('ControlName'),
                'ControlId': control_id,
                'ControlCode': control_data.get('controlCode'),
                'ControlDescription': control_data.get('ControlDescription'),
                'IsActive': control_data.get('IsActive'),
                'IsAllocated': is_allocated
            }
            try:
                result[framework_id]['controlDetails'].append(control_details)
            except:
                result[framework_id] = {'frameworkName': framework_name,
                                        'frameworkDescription': control_data.get('FrameworkDes'),
                                        'controlDetails': [control_details],
                                        'frameworkId': framework_id}
        return result

    @staticmethod
    def get_controls_framework_block_details(f_id):
        controls_query = "select c.Id as controlId, c.ControlName, c.Description as ControlDescription, c.Category," \
                         " c.ControlCode, c.IsActive as IsActive, fm.Id as frameworkId, fm.FrameworkName," \
                         " fm.Description as FrameworkDescription from ControlMaster c left join FrameworkMaster fm " \
                         " on c.FrameworkId = fm.Id"
        # controls_query = "select * from ControlMaster c left join FrameworkMaster fm  on c.FrameworkId = fm.Id"

        if f_id:
            controls_query += " where FrameworkId = {f_id}"
            controls_query = controls_query.format(f_id=str(f_id))
        framework_controls_data = fetch_data_from_sql_query(controls_query)
        result = {}
        for control_data in framework_controls_data:
            framework_id = control_data['frameworkId']
            framework_name = control_data['FrameworkName']
            control_details = {
                'ControlName': control_data.get('ControlName'),
                'ControlId': control_data.get('controlId'),
                'ControlCode': control_data.get('ControlCode'),
                'ControlDescription': control_data.get('ControlDescription'),
                'IsActive': control_data.get('IsActive'),
            }
            try:
                result[framework_id]['controlDetails'].append(control_details)
            except:
                result[framework_id] = {'frameworkName': framework_name,
                                        'frameworkDescription': control_data.get('FrameworkDescription'),
                                        'controlDetails': [control_details],
                                        'frameworkId': framework_id}
            # result[''] =
        master_frameworks = FrameworkMasterData.get_framework_master()
        for fw in master_frameworks:
            fw_id = fw.get('id')
            if not result.get(int(fw_id)):
                result[fw_id] = {'frameworkName': fw.get('framework_name'),
                                 'frameworkDescription': fw.get('description'),
                                 'controlDetails': [],
                                 'frameworkId': fw_id}
        return result


class PolicyMasterData(BaseConstant):

    @staticmethod
    def policy_details_final_object(policy_id):
        result = {}
        policy_details = PolicyMaster.objects.get(id=policy_id)
        result['policyName'] = policy_details.policy_name
        result['policyCode'] = policy_details.policy_code
        result['category'] = policy_details.category
        result['version'] = policy_details.version
        result['policySummery'] = policy_details.policy_summery


        policy_content = S3FileHandlerConstant.read_s3_content(policy_details.policy_file_name).decode("utf-8")
        result['policyContent'] = policy_content
        result['policyVariables'] = MasterPolicyParameter.objects.filter(policy_id=int(policy_id)).values('id',
                                                                                                  'policy_id',
                                                                                                  'parameter_key',
                                                                                                  'parameter_type',
                                                                                                  'is_active')
        policy_frameworks = HirerecyMapper.objects.filter(policy_id=policy_id).values('f_id')
        f_ids = set([p_f['f_id'] for p_f in policy_frameworks])
        policy_controls = HirerecyMapperData.get_selected_controls_block_details(policy_id, list(f_ids))
        result['policyControls'] = list(policy_controls.values())
        return result

    @staticmethod
    def policy_variable_handler(template_variables, policy_id, user_id):
        existing = {}
        new = []
        for variable in template_variables:
            if variable.get('id'):
                existing[int(variable.get('id'))] = variable
            else:
                entry = MasterPolicyParameter(policy_id=int(policy_id),
                                              parameter_key=variable.get('paramKey'),
                                              parameter_type=variable.get('paramType'),
                                              created_by=user_id)
                new.append(entry)

        if new:
            MasterPolicyParameter.objects.bulk_create(new)
        exiting_policies = MasterPolicyParameter.objects.filter(id__in=list(existing.keys()))
        for ex_poc in exiting_policies:
            latest = existing.get(ex_poc.id)
            ex_poc.parameter_key = latest.get('paramKey')
            ex_poc.parameter_value = latest.get('paramType')
            ex_poc.created_by = user_id
            ex_poc.save()

    @staticmethod
    def get_policy_details(query):
        policy_details = PolicyMaster.objects.filter(query).values("policy_name", "category")
        return policy_details

    @staticmethod
    def save_policy_details(data, user_id):
        policy_name = data.get('policyName')
        policy_summery = data.get('policySummery')
        policy_code = data.get('policyCode')
        content = data.get('policyContent')
        id = data.get('policyId')
        if id:
            policy_object = PolicyMaster.objects.get(id=id)
            policy_object.policy_name = policy_name
            policy_object.policy_summery = policy_summery
            policy_object.policy_code = policy_code
            policy_object.version = 1
            policy_object.user_id = user_id
            policy_object.created_by = user_id
            reference_url = S3FileHandlerConstant.upload_s3_file(content, policy_object.policy_file_name)
            policy_object.policy_reference = reference_url
        else:
            filename = 'master-policies/' + str(int(datetime.now().timestamp())) + policy_name + '.html'
            reference_url = S3FileHandlerConstant.upload_s3_file(content, filename)
            policy_object = PolicyMaster.objects.create(policy_name=policy_name,
                                                        policy_summery=policy_summery,
                                                        policy_code=policy_code,
                                                        policy_reference=reference_url,
                                                        policy_file_name=filename,
                                                        version=1,
                                                        user_id=user_id,
                                                        created_by=user_id)
        return policy_object

    @staticmethod
    def policy_control_handler(data, user_id):
        policy_id = data.get('policyId')
        framework_id = data.get('frameworkId')
        q1 = Q(f_id=int(framework_id))
        q2 = Q(policy_id=int(policy_id))
        q3 = Q(is_active=1)
        selected_controls = data.get('selectedControls')
        selected_formated_controls = {}
        for con in selected_controls:
            selected_formated_controls[int(con.get('controlId'))] = con
        existing_controls = HirerecyMapper.objects.filter(q1 & q2).values('id',
                                                                          'f_id',
                                                                          'c_id',
                                                                          'policy_id',
                                                                          'is_active')
        all_existing = {}
        active_controls = {}
        inactive_controls = {}
        for control in existing_controls:
            all_existing[control.get('c_id')] = control.get('id')
            if control.get('is_active'):
                active_controls[control.get('c_id')] = control.get('id')
            else:
                inactive_controls[control.get('c_id')] = control.get('id')
        deleted_control_ids = list(set(active_controls.keys()) - set(selected_formated_controls.keys()))
        new_control_ids = list(set(selected_formated_controls.keys() - set(all_existing.keys())))
        controls_inactive_ids = list(set(inactive_controls.keys()).intersection(set(selected_formated_controls.keys())))
        if deleted_control_ids:
            h_inactive_ids = [all_existing.get(entry) for entry in deleted_control_ids]
            HirerecyMapper.objects.filter(id__in=list(h_inactive_ids)).update(is_active=0)
        if controls_inactive_ids:
            h_active_ids = [all_existing.get(entry) for entry in controls_inactive_ids]
            HirerecyMapper.objects.filter(id__in=list(h_active_ids)).update(is_active=1)
        if new_control_ids:
            installed_controls = []
            for control_id in new_control_ids:
                new_controls = HirerecyMapper(f_id=framework_id,
                                              c_id=control_id,
                                              policy_id=policy_id,
                                              is_active=1,
                                              is_deleted=0)
                installed_controls.append(new_controls)
            if installed_controls:
                HirerecyMapper.objects.bulk_create(installed_controls)

        selected_controls = HirerecyMapperData.get_selected_controls_block_details(policy_id, [framework_id])
        return selected_controls
