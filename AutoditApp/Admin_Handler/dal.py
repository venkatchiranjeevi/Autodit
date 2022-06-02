from AutoditApp.core import fetch_data_from_sql_query
from AutoditApp.models import ControlMaster, FrameworkMaster, HirerecyMapper
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
                                               created_by = user_id)
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
    def save_frameworks(data):
        framework_obj = FrameworkMaster(framework_name=data.get("framework_name"),
                                        framework_type=data.get("framework_type"),
                                        description=data.get("description"), is_deleted=False, is_active=True,
                                        created_by=data.get("created_by"))
        framework_obj.save()
        return framework_obj


class HirerecyMapperData(BaseConstant):

    @staticmethod
    def save_hirerey_mapper_data(hirerecy_data):
        hirerecy_master_obj = HirerecyMapper(f_id=hirerecy_data.get("f_id"), c_id=hirerecy_data.get("c_id"))
        return True

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
    def get_controls_framework_block_details(f_id):
        controls_query  = "select * from ControlMaster c left join FrameworkMaster fm  on c.FrameworkId = fm.Id"
        if f_id:
            controls_query += " where FrameworkId = {f_id}"
            controls_query = controls_query.format(f_id=str(f_id))
        query_results = fetch_data_from_sql_query(controls_query)
        return query_results


class PolicyMasterData(BaseConstant):

    @staticmethod
    def get_policy_details(query):
        policy_details = PolicyMaster.objects.filter(query).values("policy_name", "category")
        return policy_details

    @staticmethod
    def save_policy_details(data):
        policy_object = PolicyMaster.objects.create(policy_name=data.get("policy_name"), category=data.get("category"),
                                                    policy_reference=data.get("policy_reference"),
                                                    version=data.get("version", 1),
                                                    user_id=data.get("user_id"), created_by=data.get("created_by"))
        return policy_object


